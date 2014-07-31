#include <time.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <strings.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/select.h>
#include <Python.h>


static
char const mystem_doc[] =
"Wrap the Yandex's mystem and provide methods for lemmatization.";


enum {
  Mystem_BUFSIZE = 1024 * 4
};


typedef struct Mystem_t {
  int pid;
  int pipe_in[2];
  int pipe_out[2];

  char *buf;
} Mystem;


static Mystem *mystem_process = NULL;


static
void Mystem_init(Mystem *self) {
  if (pipe(self->pipe_in) == -1) {
    perror("pipe(pipe_in)");
    exit(EXIT_FAILURE);
  }

  if (pipe(self->pipe_out) == -1) {
    perror("pipe(pipe_out)");
    exit(EXIT_FAILURE);
  }

  self->buf = malloc(Mystem_BUFSIZE);
  if (self->buf == NULL) {
    perror("malloc()");
    exit(EXIT_FAILURE);
  }
}

static
void Mystem_deinit(Mystem *self) {
  close(self->pipe_in[1]);
  free(self->buf);
}

static
void Mystem_execbin(Mystem *self) {
  close(self->pipe_in[1]);
  dup2(self->pipe_in[0], STDIN_FILENO);
  close(self->pipe_out[0]);
  dup2(self->pipe_out[1], STDOUT_FILENO);

  execl("/Users/negval/Downloads/mystem", "mystem",
        "-gidc",
        "--format", "json",
        "-e", "UTF-8",
        NULL);
  // execl("/usr/bin/env", "env",
  //       "cat",
  //       NULL);

  perror("execl()");
  exit(EXIT_FAILURE);
}

static
void Mystem_setup(Mystem *self) {
  close(self->pipe_in[0]);
  close(self->pipe_out[1]);

  int const flags = fcntl(self->pipe_out[0], F_GETFL);
  fcntl(self->pipe_out[0], F_SETFL, flags | O_NONBLOCK);
}

static void Mystem__write(int fd, char const *buf, size_t nbuf);
static void Mystem__read(int fd);

static
void theirstem_main(Mystem *mystem) {
  static size_t total = 2;


  int fd = mystem->pipe_in[1];
  char const buf[] = "Работаю\n";

  clock_t start, end;
  double cpu_time_used;

  start = clock();
  for (int j = 0; j < total; ++j) {
    printf("Request: %s\n", buf);
    Mystem__write(fd, buf, sizeof(buf) - 1);
    printf("Reading asnwer.\n");
    Mystem__read(mystem->pipe_out[0]);
  }
  end = clock();
  cpu_time_used = ((double) (end - start)) / CLOCKS_PER_SEC;

  fprintf(stderr, "Time was passed: %lf s\n", cpu_time_used);
  fprintf(stderr, "Speed: %lf\n", total / cpu_time_used);
}

static
void Mystem__write(int fd, char const *buf, size_t nbuf) {
  struct timeval tv;
  fd_set fds;

  for (;;) {
    tv.tv_sec = 3;
    tv.tv_usec = 0;

    FD_ZERO(&fds);
    FD_SET(fd, &fds);
    int const rv = select(fd + 1, NULL, &fds, NULL, &tv);

    if (rv == -1) {
      perror("fatal error: select()");
      exit(EXIT_FAILURE);
    }
    if (rv == 0) {
      perror("warning: select() timeout");
      continue;
    }

    if (!FD_ISSET(fd, &fds)) {
      perror("fatal error: select(): fd not in fds");
      exit(EXIT_FAILURE);
    }

    int ret = write(fd, buf, nbuf);
    if (-1 == ret && EAGAIN == errno)
      continue;

    break;
  }
}

static
void Mystem__read(int fd) {
  char buf[Mystem_BUFSIZE];
  struct timeval tv;
  fd_set fds;
  int rv;

  for (;;) {
    tv.tv_sec = 3;
    tv.tv_usec = 0;

    FD_ZERO(&fds);
    FD_SET(fd, &fds);
    rv = select(fd + 1, &fds, NULL, NULL, &tv);

    if (rv == -1) {
      perror("select()");
      exit(EXIT_FAILURE);
    }
    if (rv == 0) {
      fprintf(stderr, "warning: select() timeout\n");
      continue;
    }

    if (!FD_ISSET(fd, &fds)) {
      perror("select(): fd not in fds");
      exit(EXIT_FAILURE);
    }

    ssize_t ret = read(fd, buf, sizeof(buf));
    fprintf(stderr, "ret = %ld\n", ret);
    if (-1 == ret && EAGAIN == errno)
      continue;

    buf[ret] = '\0';
    // if (buf[ret - 1] == '\n')
      break;
  }

  printf("Answer: %s\n", buf);
}

static void
Mystem_sighandler_chld(int sig) {
  int status;
  wait(&status);
  if (!WIFEXITED(status)) {
    fprintf(stderr, "The spawned mystem process has been not normally stopped.\n");
  } else {
    fprintf(stderr, "The spawned mystem process has been terminated.\n");
  }
}

static PyObject *
mystem_start_process(PyObject *self, PyObject *args) {
  PyOS_sighandler_t handler = Mystem_sighandler_chld;
  PyOS_setsig(SIGCHLD, handler);

  mystem_process = malloc(sizeof(Mystem));
  if (mystem_process == NULL) {
    PyErr_SetNone(PyExc_MemoryError);
    Py_INCREF(Py_None);
    return Py_None;
  }

  Mystem_init(mystem_process);

  int const pid = fork();
  mystem_process->pid = pid;

  switch (pid) {
    case -1:
      perror("fatal error: fork()");
      exit(EXIT_FAILURE);

    case 0:
      Mystem_execbin(mystem_process);

    default:
      Mystem_setup(mystem_process);

      theirstem_main(mystem_process);

      break;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static
char const mystem_start_process_doc[] =
"start_process()\n\
\n\
Spawn the mystem process.";

static PyObject *
mystem_stop_process(PyObject *self, PyObject *args) {
  Mystem_deinit(mystem_process);
  free(mystem_process);
  mystem_process = NULL;

  Py_INCREF(Py_None);
  return Py_None;
}

static
char const mystem_stop_process_doc[] =
"stop_process()\n\
\n\
Stop the spawned mystem process.";

static PyObject *
mystem_tokenize(PyObject *self, PyObject *args) {
  PyObject *text;

  if (!PyArg_UnpackTuple(args, "tokenize", 1, 1, &text)) {
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static
char const mystem_tokenize_doc[] =
"tokenize(text)\n\
\n\
Return tokens for a text using Yandex's mystem.";

static PyMethodDef MystemMethods[] = {
  {"tokenize", mystem_tokenize, METH_VARARGS, mystem_tokenize_doc},
  {"start_process", mystem_start_process, METH_VARARGS, mystem_start_process_doc},
  {"stop_process", mystem_stop_process, METH_VARARGS, mystem_stop_process_doc},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initcmystem(void);

PyMODINIT_FUNC initcmystem(void)
{
  PyObject *m;

  m = Py_InitModule3("cmystem", MystemMethods, mystem_doc);
  if (m == NULL) {
    return;
  }

  return;
}


#if 0
static void
sighandler_chld(int sig) {
  int status;
  wait(&status);
  if (!WIFEXITED(status)) {
    fprintf(stderr, "The spawned mystem process has been not normally stopped.\n");
  } else {
    fprintf(stderr, "The spawned mystem process has been terminated.\n");
  }
}


int main(int argc, char **argv) {
  struct sigaction sa;
  sigemptyset(&sa.sa_mask);
  sa.sa_flags = 0;
  sa.sa_handler = sighandler_chld;
  if (sigaction(SIGCHLD, &sa, NULL) == -1) {
    perror("sigaction()");
    exit(EXIT_FAILURE);
  }

  Mystem *mystem;

  mystem = malloc(sizeof(Mystem));
  if (mystem == NULL) {
    perror("malloc()");
    exit(EXIT_FAILURE);
  }

  Mystem_init(mystem);

  int const pid = fork();
  mystem->pid = pid;

  switch (pid) {
    case -1:
      perror("fatal error: fork()");
      exit(EXIT_FAILURE);

    case 0:
      Mystem_execbin(mystem);

    default:
      Mystem_setup(mystem);

      theirstem_main(mystem);

      break;
  }

  Mystem_deinit(mystem);
  free(mystem);

  return EXIT_SUCCESS;
}
#endif
