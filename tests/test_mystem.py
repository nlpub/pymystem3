# -*- coding: utf-8 -*-

from pymystem3 import Mystem


class TestMystem(object):
    def test_mystem(self):
        m = Mystem()
        tokens = m.lemmatize("Мама мыла раму")
        assert ["мама", " ", "мыть", " ", "рама", "\n"] == tokens

    def test_mystem_not_entireinput(self):
        m = Mystem(entire_input=False)
        tokens = m.lemmatize("Мама мыла раму")
        assert ["мама", "мыть", "рама"] == tokens

    def test_mystem_abc(self):
        m = Mystem()
        tokens = m.lemmatize("ABC")
        assert ["ABC", "\n"] == tokens
