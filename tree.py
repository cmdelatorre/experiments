# Example Binary Search Tree implementation


def new_node(left_tree, value, right_tree, parent_node):
    return [left_tree, value, right_tree, parent_node]


def empty_node(parent=None):
    return new_node(None, None, None, parent)


def is_empty(tree):
    return root_value(tree) is None


def root_value(tree):
    return tree[1]


def left_branch(tree):
    return tree[0]


def right_branch(tree):
    return tree[2]


def tree_parent(tree):
    return tree[3]


def tree_add(tree, item, parent=None):
    if is_empty(tree):
        tree[0] = empty_node(parent=tree)
        tree[1] = item
        tree[2] = empty_node(parent=tree)
        tree[3] = parent
        return True
    elif item < root_value(tree):
        return tree_add(left_branch(tree), item, parent=tree)
    elif item > root_value(tree):
        return tree_add(right_branch(tree), item, parent=tree)
    else:  # item == root_value(tree)
        return False  # Item already exists


def tree_search(tree, item):
    if is_empty(tree):
        return None
    elif item < root_value(tree):
        return tree_search(left_branch(tree), item)
    elif item > root_value(tree):
        return tree_search(right_branch(tree), item)
    else:  # item == root_value(tree)
        return tree  # Item already exists


def tree_remove(tree, item):
    sub_tree = tree_search(tree, item)
    if sub_tree is None:
        return None  # item not in tree

    sub_left = left_branch(sub_tree)
    sub_right = right_branch(sub_tree)

    if is_empty(sub_right) and is_empty(sub_left):
        # Leaf case: Replace (in parent) with empty node
        parent = tree_parent(sub_tree)
        if item < root_value(parent):
            parent[0] = empty_node(parent=parent)
        else:
            parent[2] = empty_node(parent=parent)
    elif is_empty(sub_right) and not is_empty(sub_left):
        # Case Right is empty: replace (in parent) with left branch
        parent = tree_parent(sub_tree)
        parent[0] = left_branch(sub_tree)
    elif not is_empty(sub_right) and is_empty(sub_left):
        # Case Left is empty: replace (in parent) with left branch
        parent = tree_parent(sub_tree)
        parent[2] = right_branch(sub_tree)
    else:
        # No empty branch. In the right branch, search for the first empty left
        # sub-branch
        target_parent = sub_right
        target_branch = left_branch(target_parent)
        while not is_empty(target_branch):
            target_parent = target_branch
            target_branch = left_branch(target_parent)
        # Here the left sub-branch is empty: hang here the original left branch
        target_parent[0] = sub_left
        # Now, move up the rigth branch
        if sub_tree == tree:
            # Case when the root node is being deleted
            tree[0] = empty_node()
            tree[1] = sub_right[1]
            tree[2] = sub_right
        else:
            parent[2] = sub_right
