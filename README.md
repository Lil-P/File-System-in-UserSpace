# File-System-in-UserSpace
File System in UserSpace

#Summary
This is a project to develop a File System in UserSpace and make improvement step by step.<br />
The complete fusepy file could be downloaded here: https://github.com/terencehonles/fusepy.<br />
I develop it from memory.py, which locates in "example\".<br />
An empty folder, such as "fusemount", is requred to run the code and command should be like this: <br />
<b>python memory.py fusemount.</b>

#1. Support a hierarchical namespace
The original file system from the link above could have only one layer file. No file like "/dir1/xxx" exists. In order to support it, a hierarchical namespace is required.
hierarchicalFS.py is the improved code to support it.
