#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: linghanchujian

from hashlib import md5

class public_function(object):
    #md5加密
    def get_md5(self,string):
        if isinstance(string,str):
            string = string.encode("utf-8")
        m = md5()
        m.update(string)
        return m.hexdigest()
    
    #去重
    # def Duplicate_removal(self,items):
        # items["imgName_id"] = 