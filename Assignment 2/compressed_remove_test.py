import unittest
from prefix_tree import *


def repr_tree(t):
    template = "Tree({} ({})"
    subtrees = ', '.join([repr_tree(s) for s in t.subtrees])
    if subtrees:
        subtrees = ' [' + subtrees + ']'
    return template.format(t.value, float(t.weight)) + subtrees + ')'


class TestInsert(unittest.TestCase):
    def test_remove_full_match_to_empty_tree(self):
        tree = CompressedPrefixTree('sum')
        tree.insert('Hello', 2.0, ['a', 'b'])
        tree.remove(['a', 'b'])
        expected = 'Tree([] (0.0))'
        self.assertEqual(expected, repr_tree(tree))

    def test_clean_up_tree(self):
        tree = CompressedPrefixTree('sum')
        tree.insert('Hello', 2.0, ['a', 'b'])
        tree.remove([])
        expected = 'Tree([] (0.0))'
        self.assertEqual(expected, repr_tree(tree))

    def test_remove_not_exist_prefix(self):
        tree = CompressedPrefixTree('sum')
        tree.insert('Hello', 2.0, ['a', 'b'])
        tree.remove([['d']])
        expected = "Tree(['a', 'b'] (2.0) [Tree(Hello (2.0))])"
        self.assertEqual(expected, repr_tree(tree))

    def test_remove_exceeded_prefix(self):
        tree = CompressedPrefixTree('sum')
        tree.insert('Hello', 2.0, ['a', 'b'])
        tree.remove([['a', 'b', 'c']])
        expected = "Tree(['a', 'b'] (2.0) [Tree(Hello (2.0))])"
        self.assertEqual(expected, repr_tree(tree))

    def test_remove_compress_path_1(self):
        tree = CompressedPrefixTree('sum')
        tree.insert('Hello', 2.0, ['a', 'b', 'c', 'd'])
        tree.insert('bye', 4.0, ['a', 'b', 'f', 'c'])
        tree.remove(['a', 'b', 'f'])
        expected = "Tree(['a', 'b', 'c', 'd'] (2.0) [Tree(Hello (2.0))])"
        self.assertEqual(expected, repr_tree(tree))

    def test_remove_compress_path_2(self):
        tree = CompressedPrefixTree('sum')
        tree.insert('Hello', 2.0, ['a', 'b', 'c', 'd'])
        tree.insert('Hey', 2.0, ['a', 'b', 'c', 'q'])
        tree.insert('bye', 4.0, ['a', 'b', 'f', 'c'])
        tree.remove(['a', 'b', 'f'])
        expected = "Tree(['a', 'b', 'c'] (4.0) [Tree(['a', 'b', 'c', 'd'] (2.0)" \
                   " [Tree(Hello (2.0))]), Tree(['a', 'b', 'c', 'q'] (2.0) [Tree(Hey (2.0))])])"
        self.assertEqual(expected, repr_tree(tree))

    def test_remove_compress_to_root(self):
        tree = CompressedPrefixTree('sum')
        tree.insert('Hello', 2.0, ['c', 'd'])
        tree.insert('Hey', 2.0, ['a', 'b', 'c', 'q'])
        tree.remove(['a', 'b'])
        expected = "Tree(['c', 'd'] (2.0) [Tree(Hello (2.0))])"
        self.assertEqual(expected, repr_tree(tree))

    def test_remove_no_compress(self):
        tree = CompressedPrefixTree('sum')
        tree.insert('Hello', 2.0, ['a', 'b'])
        tree.insert('Hey', 2.0, ['a', 'b', 'c', 'q'])
        tree.remove(['a', 'b', 'c', 'q'])
        expected = "Tree(['a', 'b'] (2.0) [Tree(Hello (2.0))])"
        self.assertEqual(expected, repr_tree(tree))


if __name__ == "__main__":
    unittest.main(exit=False)