"""Builds the original sample course used for the demo and evaluation."""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

PAGES = [
("Lecture 1: Algorithm Complexity", [
"Big O notation describes how the running time of an algorithm grows as the input size n grows. It ignores constant factors and focuses on the dominant term, so 3n + 10 is written as O(n).",
"Common growth rates, from fastest to slowest, are O(1) constant, O(log n) logarithmic, O(n) linear, O(n log n) linearithmic, O(n^2) quadratic, and O(2^n) exponential.",
"Worst-case complexity is the longest time an algorithm can take on any input of size n. Average-case complexity is the expected time over typical inputs. Space complexity measures the extra memory an algorithm needs."]),
("Lecture 2: Arrays", [
"An array stores elements of the same type in contiguous memory locations. Because the address of any element can be calculated from its index, reading an element by index takes O(1) time.",
"Inserting or deleting an element in the middle of an array takes O(n) time because the following elements must be shifted.",
"A static array has a fixed size chosen when it is created. A dynamic array grows by allocating a larger block, usually double the size, and copying the elements. Appending to a dynamic array takes amortized O(1) time."]),
("Lecture 3: Linked Lists", [
"A singly linked list is a sequence of nodes, where each node holds a value and a pointer to the next node. The last node points to null, and the head pointer marks the first node.",
"Accessing the k-th element of a linked list takes O(k) time because the list must be traversed from the head. Inserting at the head takes O(1) time because only pointers change.",
"Compared with an array, a linked list uses extra memory for pointers and has poor cache locality, but it does not need contiguous memory and does not shift elements on insertion."]),
("Lecture 4: Stacks", [
"A stack is a Last In, First Out (LIFO) structure: the most recently added item is removed first. Its main operations are push, which adds an item to the top, pop, which removes the top item, and peek, which reads it without removing it.",
"All three stack operations take O(1) time when the stack is implemented with an array or a linked list.",
"Stacks are used to manage function calls through the call stack, to evaluate expressions, to check balanced parentheses, and to implement undo features. A stack overflow happens when recursion is too deep and the call stack runs out of space."]),
("Lecture 5: Queues", [
"A queue is a First In, First Out (FIFO) structure: the earliest added item is removed first. Enqueue adds an item at the rear, and dequeue removes an item from the front.",
"A circular queue stores items in a fixed array and wraps the rear and front indexes around to reuse free slots. Both enqueue and dequeue take O(1) time.",
"Queues are used for task scheduling, print jobs, and handling requests in the order they arrive. A priority queue is different: it removes the item with the highest priority, not the oldest one, and is commonly implemented with a heap."]),
("Lecture 6: Binary Search Trees", [
"A binary tree is a hierarchy in which every node has at most two children. The top node is the root, and a node with no children is a leaf. The height of a tree is the number of edges on the longest path from the root to a leaf.",
"In a binary search tree, every key in the left subtree is smaller than the node's key, and every key in the right subtree is larger. An inorder traversal of a binary search tree visits the keys in sorted order.",
"Search, insertion, and deletion take O(h) time, where h is the tree height. A balanced tree has height O(log n), but inserting sorted keys into a plain binary search tree can make it degenerate, with height O(n)."]),
("Lecture 7: Hash Tables", [
"A hash table stores key-value pairs. A hash function converts a key into an index in an underlying array, which gives average O(1) time for search, insertion, and deletion.",
"A collision happens when two different keys map to the same index. Chaining resolves collisions by keeping a linked list at each index. Open addressing resolves them by probing for another free slot in the array.",
"The load factor is the number of stored items divided by the number of slots. When the load factor gets too high, performance drops, so the table is resized and all keys are rehashed. In the worst case, when many keys collide, an operation takes O(n) time."]),
("Lecture 8: Searching and Sorting", [
"Linear search checks elements one by one and takes O(n) time. Binary search works only on a sorted array: it compares the target with the middle element and discards half of the range at each step, which takes O(log n) time.",
"Bubble sort repeatedly swaps adjacent elements that are out of order and takes O(n^2) time in the worst case.",
"Merge sort divides the array into two halves, sorts each half recursively, and merges the results. It takes O(n log n) time in all cases and needs O(n) extra space. A sorting algorithm is stable when equal elements keep their original relative order."]),
]


def main():
    out = Path(__file__).resolve().parent.parent / "course" / "data_structures_notes.pdf"
    styles = getSampleStyleSheet()
    story = []
    for i, (title, paragraphs) in enumerate(PAGES):
        story.append(Paragraph(title, styles["Heading1"]))
        for p in paragraphs:
            story += [Paragraph(p, styles["BodyText"]), Spacer(1, 10)]
        if i < len(PAGES) - 1:
            story.append(PageBreak())
    SimpleDocTemplate(str(out), pagesize=A4, title="Data Structures Notes").build(story)
    print(out)


if __name__ == "__main__":
    main()
