#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import logging

from collections import defaultdict
from errno import *
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

if not hasattr(__builtins__, 'bytes'):
    bytes = str

#block size
blocksize = 5

#split string into seperate block in format of list
def string_to_datalist(s):
    listInBlock = []
    stringLength = len(s)
    times = stringLength/blocksize
    times = int(times)
    print(times)
    for i in range(times+1):
        listInBlock.append(s[blocksize*i:blocksize*i+blocksize])
    print(listInBlock)
    return listInBlock

#convert datalist into string 
def datalist_to_string(l):
    stringRead = ''
    for i in range(len(l)):
        stringRead += l[i]
    return stringRead

#function to provide parent dict interface
def GetParentDir_TargetFile(memoryObject, path):
    rootDir = '/'
    pathString = path[1:]
    pathList = pathString.split('/')
    targetFile = pathList[len(pathList)-1]
    parentList = pathList[:len(pathList)-1]
    parentDict = memoryObject.files['/']
    for _dir in parentList:
        parentDict = parentDict['content'][_dir]
    #print('parentDist: ', parentDict)
    #print('targetFile: ', targetFile)
    return[parentDict, targetFile]

class Memory(LoggingMixIn, Operations):

    def __init__(self):
        self.files = {}
        #self.data = defaultdict(bytes)
        self.fd = 0
        now = time()
        self.files['/'] = dict(st_mode=(S_IFDIR | 0o755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2, content={})

    def chmod(self, path, mode):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)
        parentDict['content'][targetFile]['st_mode'] &= 0o770000
        parentDict['content'][targetFile]['st_mode'] |= mode
        '''
        self.files[path]['st_mode'] &= 0o770000
        self.files[path]['st_mode'] |= mode
        '''
        return 0

    def chown(self, path, uid, gid):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)
        parentDict['content'][targetFile]['st_uidst_mode'] = uid
        parentDict['content'][targetFile]['st_uidst_mode'] = gid
        '''
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid
        '''

    def create(self, path, mode):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)
        parentDict['content'][targetFile] = dict(st_mode=(S_IFREG | mode), st_nlink=1,
                                                 st_size=0, st_ctime=time(), st_mtime=time(),
                                                 st_atime=time(), data=[])
        '''        
        self.files[path] = dict(st_mode=(S_IFREG | mode), st_nlink=1,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time())
        '''
        self.fd += 1
        return self.fd

    def getattr(self, path, fh=None):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)
        #print(parentDict)
        #print(targetFile)

        if path == '/':
            return self.files['/']
        else:
            if targetFile not in parentDict['content']:
                raise FuseOSError(ENOENT)
            return parentDict['content'][targetFile]

        '''
        if path not in self.files:
            raise FuseOSError(ENOENT)
        
        return self.files[path]
        '''
        
    
    def getxattr(self, path, name, position=0):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)

        attrs = parentDict['content'][targetFile].get('attrs',{})

        try:
            return attrs[name]
        except KeyError:
            return ''
        
        '''
        attrs = self.files[path].get('attrs', {})

        try:
            return attrs[name]
        except KeyError:
            return ''       # Should return ENOATTR
        '''

        
    def listxattr(self, path):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)

        attrs = parentDict['content'][targetFile].get('attrs',{})
        '''
        attrs = self.files[path].get('attrs', {})
        '''
        return attrs.keys()

    def mkdir(self, path, mode):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)

        parentDict['content'][targetFile] = dict(st_mode=(S_IFDIR | mode), st_nlink=2,
                                                 st_size=0, st_ctime=time(), st_mtime=time(),
                                                 st_atime=time(), content={})

        parentDict['st_nlink'] += 1
        '''
        self.files[path] = dict(st_mode=(S_IFDIR | mode), st_nlink=2,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time())

        self.files['/']['st_nlink'] += 1
        '''

        
    def open(self, path, flags):
        #parentDict, targetFile = GetParentDir_TargetFile(self, path)
        # nothing need to change
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)
        stringRead = datalist_to_string(parentDict['content'][targetFile]['data'])
        return stringRead[offset:offset + size]

        '''
        return self.data[path][offset:offset + size]
        '''
    def readdir(self, path, fh):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)

        if path == '/':
            return ['.', '..'] + [x for x in self.files['/']['content']]
        else:
            return ['.', '..'] + [x for x in parentDict['content'][targetFile]['content']]

        '''
        return ['.', '..'] + [x[1:] for x in self.files if x != '/']
        '''
    def readlink(self, path):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)
        stringRead = datalist_to_string(parentDict['content'][targetFile]['data'])
        return stringRead

        '''
        return self.data[path]
        '''
    def removexattr(self, path, name):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)
        attrs = parentDict['content'][targetFile].get('attrs', {})

        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

        '''
        attrs = self.files[path].get('attrs', {})

        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR
        '''
    def rename(self, old, new):
        old_parentDict, old_targetFile = GetParentDir_TargetFile(self, old)
        new_parentDict, new_targetFile = GetParentDir_TargetFile(self, new)

        new_parentDict['content'][new_targetFile] = old_parentDict['content'].pop(old_targetFile)

        '''self.files[new] = self.files.pop(old)'''

    def rmdir(self, path):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)
        if(len(parentDict['content'][targetFile]['content']) == 0):
            parentDict['content'].pop(targetFile)
            parentDict['st_nlink'] -= 1
        else:
            raise FuseOSError(ENOTDIR)
        '''
        self.files.pop(path)
        self.files['/']['st_nlink'] -= 1
        '''
        
    def setxattr(self, path, name, value, options, position=0):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)
        attrs = parentDict['content'][targetFile].setdefault('attrs', {})
        attrs[name] = value

        '''
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value
        '''

    def statfs(self, path):
        #parentDict, targetFile = GetParentDir_TargetFile(self, path)
        
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        target_parentDict, target_targetFile = GetParentDir_TargetFile(self, target)
        #source_parentDict, source_targetFile = GetParentDir_TargetFile(self, source)
        target_parentDict['content'][target_targetFile] = dict(st_mode=(S_IFLNK | 0o777), st_nlink=1,
                                                               st_size=len(source), data = [])
        target_parentDict['content'][target_targetFile]['data'] = string_to_datalist(source) 
        
        '''
        self.files[target] = dict(st_mode=(S_IFLNK | 0o777), st_nlink=1,
                                  st_size=len(source))

        self.data[target] = source
        '''

    def truncate(self, path, length, fh=None):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)
        stringRead = datalist_to_string(parentDict['content'][targetFile]['data'])
        stringRead = stringRead[:length]
        newDataList = string_to_datalist(stringRead)
        parentDict['content'][targetFile]['data'] = newDataList
        parentDict['content'][targetFile]['st_size'] = length

        '''
        self.data[path] = self.data[path][:length]
        self.files[path]['st_size'] = length
        '''

    def unlink(self, path):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)
        parentDict['content'].pop(targetFile)
        
        '''self.files.pop(path)'''

    def utimens(self, path, times=None):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)
        now = time()
        atime, mtime = times if times else (now, now)
        parentDict['content'][targetFile]['st_atime'] = atime
        parentDict['content'][targetFile]['st_mtime'] = mtime
        
        '''
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime
        '''

    def write(self, path, data, offset, fh):
        parentDict, targetFile = GetParentDir_TargetFile(self, path)
        stringRead = datalist_to_string(parentDict['content'][targetFile]['data'])
        print("stringRead:::::", stringRead)
        newString = stringRead[:offset] + data
        print("newString:::::", newString)
        parentDict['content'][targetFile]['data'] = string_to_datalist(newString)
        parentDict['content'][targetFile]['st_size'] = len(newString)
        return len(data)


        '''
        self.data[path] = self.data[path][:offset] + data
        self.files[path]['st_size'] = len(self.data[path])
        return len(data)
        '''


if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(Memory(), argv[1], foreground=True)
