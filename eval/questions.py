"""Evaluation questions. `page` is the page holding the answer; None means the course does not cover it.
Thresholds are tuned on `dev`. `test` is only for the final score."""
DEV = [
("What does Big O notation describe?",1),("ايه هو Big O؟",1),("What is space complexity?",1),("ايه هو التعقيد المكاني؟",1),
("Why is reading an array element by index O(1)?",2),("ليه الاضافة في نص الارراي بطيئة؟",2),("How does a dynamic array grow?",2),
("What does a node hold in a singly linked list?",3),("ايه عيوب اللينكد ليست مقارنة بالارراي؟",3),
("What does LIFO mean?",4),("ايه هو الستاك؟",4),("What causes a stack overflow?",4),
("What is the difference between enqueue and dequeue?",5),("يعني ايه طابور دائري؟",5),
("What is a leaf node in a tree?",6),("ايه شرط شجرة البحث الثنائية؟",6),
("How does chaining resolve collisions?",7),("يعني ايه تصادم في جدول الهاش؟",7),("What is the load factor?",7),
("Why must binary search use a sorted array?",8),("ازاي بيشتغل البحث الثنائي؟",8),("What makes a sorting algorithm stable?",8),
("ايه الفرق بين الستاك والكيو؟",4),("What is the capital of France?",None),("ايه عاصمة مصر؟",None),("How does the TCP handshake work?",None),("اشرحلي الـ blockchain",None),
("What is Dijkstra's shortest path algorithm?",None),("How do I center a div in CSS?",None),("ايه هو الـ deep learning؟",None),("Who won the 2022 World Cup?",None),
]
TEST = [
("What growth rate is O(n log n) called?",1),("يعني ايه اسوأ حالة في التعقيد؟",1),("What is amortized O(1) appending?",2),("ايه الفرق بين static array و dynamic array؟",2),
("How long does it take to insert at the head of a linked list?",3),("ازاي بنوصل لعنصر في القائمة المترابطة؟",3),("What are the push and pop operations?",4),("الستاك بيتستخدم في ايه؟",4),
("What does FIFO mean for a queue?",5),("ايه هو طابور الاولوية؟",5),("How is a priority queue usually implemented?",5),("What does an inorder traversal of a BST produce?",6),
("ايه هو ارتفاع الشجرة؟",6),("What happens when sorted keys are inserted into a plain binary search tree?",6),("What does a hash function do?",7),("ايه هو معامل التحميل في الهاش تيبل؟",7),
("What is open addressing?",7),("When is a hash table resized?",7),("How does merge sort work?",8),("كام زمن بابل سورت؟",8),("ايه الفرق بين البحث الخطي والبحث الثنائي؟",8),
("How do I train a neural network?",None),("What is SQL injection?",None),("ايه هي نظرية فيثاغورس؟",None),("What is the OSI model?",None),("ازاي اعمل موقع بـ React؟",None),("What is the boiling point of water?",None),("ايه هو الـ Kubernetes؟",None),("How does a red-black tree rebalance?",None),("What is Python's GIL?",None),
]
