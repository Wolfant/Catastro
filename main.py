#!/bin/python
'''
Created on May 29, 2017

@author: Antonio Insuasti
'''
import sys
import os
import pprint
#from ec.gob.sri.cco.mongodbutils.mongodbutil import MongoDbUtil
from StandaloneData import StandaloneData

def json2html(jdata):
    htmltxt = "<table><tr><td>runtime-name</td><td>name</td></tr>"
    for deploy in jdata:
        for attribute, value in deploy.iteritems():
		if attribute == "runtime-name":
			htmltxt +="<tr><td>{}</td>".format(value)
		if attribute == "name":
			htmltxt +="<td>{}</td></tr>".format(value)
	
    htmltxt += "</table>"
    return (str(htmltxt))

def main():
    try:
        file = sys.argv[1]
    except IndexError:
        print "Need file to parse"
        sys.exit(1)

    if not os.access(file, os.R_OK):
        print "I Can't read {}".format(sys.argv[1])
        sys.exit(1)
        
    jbserver, jbinstance = file.replace('.xml', '').replace("test/",'').split("-")
    xmldata = StandaloneData()
    jdata = xmldata.loadData(file,"6")
    jdata = xmldata.extractDsJb6()
    deploy = xmldata.extractDeployments()
    jbsdata = {'server': jbserver, 
               'instance': jbinstance, 
               'datasources': jdata,
               'Deployments': deploy }
    
    pprint.pprint(json2html(deploy))

if __name__ == '__main__':
    main()
