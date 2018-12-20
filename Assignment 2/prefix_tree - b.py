"""CSC148 Assignment 2: Autocompleter classes

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This file contains the design of a public interface (Autocompleter) and two
implementation of this interface, SimplePrefixTree and CompressedPrefixTree.
You'll complete both of these subclasses over the course of this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
from typing import Any, List, Optional, Tuple


################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """
    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        raise NotImplementedError

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree (Tasks 1-3)
################################################################################
def my_sorted(lst: List[Tuple[Any, float]]) -> List[Tuple[Any, float]]:
    """A helper function to put auto complete result in order.
    """
    for _ in range(len(lst)):
        for j in range(len(lst) - 1):
            if lst[j][1] < lst[j+1][1]:
                lst[j], lst[j+1] = lst[j+1], lst[j]
    return lst

class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    This class follows the implementation described on the assignment handout.
    Note that we've made the attributes public because we will be accessing them
    directly for testing purposes.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - ("prefixes grow by 1")
      If len(self.subtrees) > 0, and subtree in self.subtrees, and subtree
      is non-empty and not a leaf, then

          subtree.value == self.value + [x], for some element x

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    subtrees: List[SimplePrefixTree]
    w_type: str
    length: int
    lfweight: float

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.value = []
        self.weight = 0
        self.subtrees = []
        self.w_type = weight_type
        self.length = 0
        self.lfweight = 0

    def __len__(self) -> int:
        """Determine the length of a simple prefix tree.
        """
        if self.subtrees == []:
            if self.weight == 0:
                return 0
            else:
                return 1
        else:
            s = 0
            for sub in self.subtrees:
                if sub.length > 0:
                    s += sub.length
                elif sub.length == 0:
                    s += len(sub)
                else:
                    pass
            self.length = s
            return s

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.
        """
        if prefix == self.value:    # Ready to add a leaf.
            the_leaf = SimplePrefixTree(self.w_type)
            the_leaf.value = value
            the_leaf.weight = weight
            the_leaf.length = 1
            the_leaf.lfweight = weight
            # There are two ways to add a leaf:
            # 1. The leaf already exists in current subtree.
            #    Add its weight to the leaf. Re-arrange the subtrees by their
            #    weights.
            # 2. The leaf is not in this subtree. Append this leaf onto the
            #    subtree, re-arrange the subtrees by weights.
            state = 2
            for sub in self.subtrees:
                if sub.value == the_leaf.value:
                    sub.weight += weight
                    sub.lfweight += weight
                    state = 1
            if state == 2:
                self.subtrees.append(the_leaf)
        else:
            if prefix[0:len(self.value)] == self.value:
                # If the current node is the value's prefix, then either:
                # 1. The value should be inserted under one of current node's
                #    subtrees, where that tree is also the value's prefix.
                # 2. None of the node's subtrees is the value's prefix, so
                #    the value should be put directly under current node.
                # Since this is a Simple Prefix Tree, prefix starts from [].
                # That means the if block will always run and insert the value
                # somewhere in the tree.
                # Same idea does NOT work for Compressed Trees.
                inserted = False
                for sub in self.subtrees:
                    if prefix[0:len(sub.value)] == sub.value:
                        sub.insert(value, weight, prefix)
                        inserted = True
                if not inserted:
                    the_node = SimplePrefixTree(self.w_type)
                    the_node.value = prefix[0:(len(self.value)+1)]
                    the_node.insert(value, weight, prefix)
                    self.subtrees.append(the_node)
        self.rearrange()

    def rearrange(self) -> None:
        """This function does three things:
        1. Put all subtrees in non-increasing order.
        2. Calculate the correct weight of the current node.
        3. remove all subtrees that have zero weight.

        But before doing these two things, it will rearrange all its subtrees.
        Has no effect on leaves or empty trees.
        """
        if self.subtrees == []:
            return
        else:
            # Calculate the current node's weight base on its type.
            # Note that all its subtree's weight has been calculated already.
            if self.w_type == 'sum':
                s = 0
                for sub in self.subtrees:
                    s += sub.weight
                self.weight = s
                self.lfweight = s
            else:
                if len(self) == 0:
                    self.weight = 0
                    self.lfweight = -1
                    # This is to allow temporary empty nodes.
                else:
                    self.lfweight = self.leaf_weight()
                    self.weight = self.lfweight / len(self)
            # Now use a slow but neat bubble sort, put the subtrees in a
            # non-increasing order. Note that all subtrees' subtrees have
            # already been arranged.
            for _ in range(len(self.subtrees)):
                for j in range(len(self.subtrees) - 1):
                    if self.subtrees[j].weight < self.subtrees[j+1].weight:
                        self.subtrees[j], self.subtrees[j+1] = \
                            self.subtrees[j+1], self.subtrees[j]
            # Now if there's any empty subtrees under current node, remove them.
            # Again, no need to worry about deeper empty trees because they
            # have already been removed, because all subtrees have been
            # rearranged already.
            for sub in reversed(self.subtrees):
                if sub.weight == 0:
                    self.subtrees.remove(sub)


    def leaf_weight(self) -> float:
        """To calculate the leaf weight of a node using memoization.
        """
        if self.subtrees == []:
            return self.weight
        else:
            s = 0
            for sub in self.subtrees:
                if sub.lfweight > 0:
                    s += sub.lfweight
                elif sub.lfweight == 0:
                    s += sub.leaf_weight()
                else:
                    pass
            self.lfweight = s
            return s

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.
        """
        if prefix == []:
            if limit is None:
                return my_sorted(self.return_all_leaves())
            else:
                return my_sorted(self.return_limited_leaves(limit))
        if self.subtrees == []:
            return []
        if limit is None:
            return my_sorted(self.unlimited_autocomplete(prefix))
        else:
            return my_sorted(self.limited_autocomplete(prefix, limit))

    def unlimited_autocomplete(self, prefix: List) -> List[Tuple[Any, float]]:
        """Helper function of autocomplete, used for unlimited auto completion.
        """
        lst = []
        if prefix[0:len(self.value)] == self.value:
            for sub in self.subtrees:
                if sub.subtrees != []:
                    if sub.value[0:len(prefix)] == prefix:
                        lst.extend(sub.return_all_leaves())
                        break
                    elif prefix[0:len(sub.value)] == sub.value:
                        lst.extend(sub.unlimited_autocomplete(prefix))
                        break
        return lst

    def limited_autocomplete(self, prefix: List, limit: int) -> \
            List[Tuple[Any, float]]:
        """Helper function of autocomplete, used for limited auto completion.
        """
        lst = []
        if prefix[0:len(self.value)] == self.value:
            for sub in self.subtrees:
                if sub.subtrees != []:
                    if sub.value[0:len(prefix)] == prefix:
                        a = sub.return_limited_leaves(limit)
                        lst.extend(a)
                        break
                    elif prefix[0:len(sub.value)] == sub.value:
                        lst.extend(sub.limited_autocomplete(prefix, limit))
                        break
        return lst

    def return_all_leaves(self) -> List[Tuple[Any, float]]:
        """Return all leaves of a tree, from left to right.
        """
        lst = []
        if self.subtrees == [] and self.weight == 0:
            return []
        if self.subtrees == [] and self.weight > 0:
            lst.append((self.value, self.weight))
            return lst
        for sub in self.subtrees:
            lst.extend(sub.return_all_leaves())
        return lst

    def return_limited_leaves(self, limit: int) -> List[Tuple[Any, float]]:
        """Return given number of leaves from left to right.
        """
        if limit <= 0:
            return []
        else:
            lst = []
            if self.subtrees == [] and self.weight > 0:
                lst.append((self.value, self.weight))
                return lst
            for sub in self.subtrees:
                a = sub.return_limited_leaves(limit)
                lst.extend(a)
                limit -= len(a)
        return lst

    def remove(self, prefix: List) -> None:
        """Remove all values matching the prefix.
        """
        if prefix == []:
            self.length = 0
            self.lfweight = -1
            self.weight = 0
            self.subtrees = []
            self.value = 0
        if self.subtrees == []:
            return
        if prefix[0:len(self.value)] == self.value:
            for sub in self.subtrees:
                if sub.subtrees != []:
                    if sub.value[0:len(prefix)] == prefix:
                        sub.weight = 0
                        sub.lfweight = -1
                        sub.length = -1
                    else:
                        sub.remove(prefix)
        self.rearrange()


################################################################################
# CompressedPrefixTree (Task 6)
################################################################################
def lcp(lst1: List[Any], lst2: List[Any]) -> List[Any]:
    """A function used to determine "Longest Common Prefix" of two lists.
    """
    new_l = []
    for i in range(len(lst1)):
        if (i + 1) > len(lst2):
            break
        elif lst1[i] == lst2[i]:
            new_l.append(lst1[i])
        else:
            break
    return new_l

class CompressedPrefixTree(Autocompleter):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version follows the implementation
    described on Task 6 of the assignment handout, which reduces the number of
    tree objects used to store values in the tree.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - **NEW**
      This tree does not contain any compressible internal values.
      (See the assignment handout for a definition of "compressible".)

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Optional[Any]
    weight: float
    subtrees: List[CompressedPrefixTree]
    w_type: str
    length: int
    lfweight: float

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.value = []
        self.weight = 0
        self.subtrees = []
        self.w_type = weight_type
        self.length = 0
        self.lfweight = 0

    def __len__(self) -> int:
        """Determine the length of a compressed tree.
        """
        if self.subtrees == []:
            if self.weight == 0:
                return 0
            else:
                return 1
        else:
            s = 0
            for sub in self.subtrees:
                if sub.length > 0:
                    s += sub.length
                elif sub.length == 0:
                    s += len(sub)
                else:
                    pass
            self.length = s
            return s


    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.
        """
        if prefix == self.value:  # Ready to add a leaf.
            the_leaf = CompressedPrefixTree(self.w_type)
            the_leaf.value = value
            the_leaf.weight = weight
            the_leaf.length = 1
            the_leaf.lfweight = weight
            # There are two ways to add a leaf:
            # 1. The leaf already exists in current subtree.
            #    Add its weight to the leaf. Re-arrange the subtrees by their
            #    weights.
            # 2. The leaf is not in this subtree. Append this leaf onto the
            #    subtree, re-arrange the subtrees by weights.
            # This part shall NOT change for Compressed Trees.
            state = 2
            for sub in self.subtrees:
                if sub.value == the_leaf.value:
                    sub.lfweight += weight
                    sub.weight += weight
                    state = 1
            if state == 2:
                self.subtrees.append(the_leaf)
        elif prefix[0:len(self.value)] != self.value:
            node1 = CompressedPrefixTree(self.w_type)
            node1.value = lcp(self.value, prefix)
            node2 = CompressedPrefixTree(self.w_type)
            node2.value = prefix
            node2.insert(value, weight, prefix)
            node3 = CompressedPrefixTree(self.w_type)
            node3.subtrees = self.subtrees
            node3.value = self.value
            node3.weight = self.weight
            node3.lfweight = self.lfweight
            node1.subtrees.append(node3)
            node1.subtrees.append(node2)
            self.subtrees = node1.subtrees
            self.value = node1.value
        else:
            if self.value == [] and self.subtrees == []:
                self.value = prefix
                self.insert(value, weight, prefix)
            else:
                inserted = False
                for sub in self.subtrees:
                    if len(lcp(sub.value, prefix)) \
                            > len(lcp(self.value, prefix)):
                        sub.insert(value, weight, prefix)
                        inserted = True
                if not inserted:
                    node = CompressedPrefixTree(self.w_type)
                    node.value = prefix
                    node.insert(value, weight, prefix)
                    self.subtrees.append(node)
        self.rearrange()

    def rearrange(self) -> None:
        """This function does three things:
        1. Put all subtrees in non-increasing order.
        2. Calculate the correct weight of the current node.
        3. remove all subtrees that have zero weight.

        But before doing these two things, it will rearrange all its subtrees.
        Has no effect on leaves or empty trees.
        """
        if self.subtrees == []:
            return
        else:
            # Calculate the current node's weight base on its type.
            # Note that all its subtree's weight has been calculated already.
            if self.w_type == 'sum':
                s = 0
                for sub in self.subtrees:
                    s += sub.weight
                self.weight = s
                self.lfweight = s
            else:
                if len(self) == 0:
                    self.weight = 0
                    self.lfweight = 0
                    # This is to allow temporary empty nodes.
                else:
                    self.lfweight = self.leaf_weight()
                    self.weight = self.leaf_weight() / len(self)
            # Now use a slow but neat bubble sort, put the subtrees in a
            # non-increasing order. Note that all subtrees' subtrees have
            # already been arranged.
            for _ in range(len(self.subtrees)):
                for j in range(len(self.subtrees) - 1):
                    if self.subtrees[j].weight < self.subtrees[j + 1].weight:
                        self.subtrees[j], self.subtrees[j + 1] = \
                            self.subtrees[j + 1], self.subtrees[j]
            # Now if there's any empty subtrees under current node, remove them.
            # Again, no need to worry about deeper empty trees because they
            # have already been removed, because all subtrees have been
            # rearranged already.

            # # After removing some value, there may be redundant branches
            # # which are not allowed in Compressed Trees. Look for the branches
            # # where it has one subtree and that subtree is also an internal
            # # value. If found, promote that subtree.
            for sub in reversed(self.subtrees):
                if sub.weight == 0:
                    self.subtrees.remove(sub)
            if len(self.subtrees) == 1 and len(self.subtrees[0].subtrees) > 0:
                self.weight = self.subtrees[0].weight
                self.lfweight = self.subtrees[0].lfweight
                self.value = self.subtrees[0].value
                self.subtrees = self.subtrees[0].subtrees

    def leaf_weight(self) -> float:
        """A function used to calculate leaf weight of a tree, with memoization.
        """
        if self.subtrees == []:
            return self.weight
        else:
            s = 0
            for sub in self.subtrees:
                if sub.lfweight > 0:
                    s += sub.lfweight
                elif sub.lfweight == 0:
                    s += sub.leaf_weight()
                else:
                    pass
            self.lfweight = s
            return s

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Auto complete method for compressed trees.
        """
        if prefix == []:
            if limit is None:
                return my_sorted(self.return_all_leaves())
            else:
                return my_sorted(self.return_limited_leaves(limit))
        if self.subtrees == []:
            return []
        if limit is None:
            return my_sorted(self.unlimited_autocomplete(prefix))
        else:
            return my_sorted(self.limited_autocomplete(prefix, limit))

    def unlimited_autocomplete(self, prefix: List) -> List[Tuple[Any, float]]:
        """A helper function for unlimited autocomplete.
        """
        lst = []
        if self.value[0:len(prefix)] == prefix:
            x = self.return_all_leaves()
            lst.extend(x)
        if prefix[0:len(self.value)] == self.value:
            for sub in self.subtrees:
                if sub.subtrees != []:
                    if sub.value[0:len(prefix)] == prefix:
                        lst.extend(sub.return_all_leaves())
                        break
                    elif prefix[0:len(sub.value)] == sub.value:
                        lst.extend(sub.unlimited_autocomplete(prefix))
                        break
        return lst

    def limited_autocomplete(self, prefix: List, limit: int) -> \
            List[Tuple[Any, float]]:
        """A helper function for limited autocomplete.
        """
        lst = []
        if self.value[0:len(prefix)] == prefix:
            x = self.return_limited_leaves(limit)
            lst.extend(x)
        elif prefix[0:len(self.value)] == self.value:
            for sub in self.subtrees:
                if sub.subtrees != []:
                    if sub.value[0:len(prefix)] == prefix:
                        a = sub.return_limited_leaves(limit)
                        lst.extend(a)
                        break
                    elif prefix[0:len(sub.value)] == sub.value:
                        lst.extend(sub.limited_autocomplete(prefix, limit))
                        break
        return lst

    def return_all_leaves(self) -> List[Tuple[Any, float]]:
        """Return all leaves of a tree, from left to right.
        """
        lst = []
        if self.subtrees == [] and self.weight == 0:
            return []
        if self.subtrees == [] and self.weight > 0:
            lst.append((self.value, self.weight))
            return lst
        for sub in self.subtrees:
            lst.extend(sub.return_all_leaves())
        return lst

    def return_limited_leaves(self, limit: int) -> List[Tuple[Any, float]]:
        """Return given number of leaves of a tree. From left to right.
        """
        if limit <= 0:
            return []
        else:
            lst = []
            if self.subtrees == [] and self.weight > 0:
                lst.append((self.value, self.weight))
                return lst
            for sub in self.subtrees:
                a = sub.return_limited_leaves(limit)
                lst.extend(a)
                limit -= len(a)
        return lst

    def remove(self, prefix: List) -> None:
        """Remove all matching results from a tree, with a matching prefix.
        """
        if self.subtrees == []:
            return
        if prefix == []:
            self.value = []
            self.subtrees = []
            self.weight = 0
            self.lfweight = -1
            return
        if self.value[0:len(prefix)] == prefix:
            self.value = []
            self.subtrees = []
            self.weight = 0
            self.lfweight = -1
        elif prefix[0:len(self.value)] == self.value:
            for sub in self.subtrees:
                if sub.subtrees != []:
                    if sub.value[0:len(prefix)] == prefix:
                        sub.weight = 0
                        sub.lfweight = -1
                        sub.length = -1
                    else:
                        sub.remove(prefix)
        self.rearrange()


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'max-nested-blocks': 4
    })
