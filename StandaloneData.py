'''
Created on 29 may. 2017

@author: Antonio Insuasti
'''

import re
import xml.etree.ElementTree as ET


class StandaloneData:

    subsystems = None
    sub_ds = None
    seDomains = None
    tree = None
    jbossxml = None
    texturl = None
    deployments = None
    dictds = []
    dicdeploy = []

    def __init__(self):
        pass

    def loadData(self, standalonexml, version):
        if version == "6":
            self.tree = ET.parse(standalonexml)
            self.jbossxml = self.tree.getroot()
            for child in self.jbossxml:
                if child.tag == "{urn:jboss:domain:1.5}profile":
                    self.subsystems = child
            for child in self.subsystems:
                if child.tag == "{urn:jboss:domain:datasources:1.1}subsystem":
                    self.sub_ds = child[0]

                if child.tag == "{urn:jboss:domain:security:1.2}subsystem":
                    self.seDomains = child[0]
        else:
            # TO-DO
            # IF JBoss is 6.
            self.tree = None
            self.jbossxml = None
            self.subsystem = None
            self.sub_ds = None
            self.seDomains = None
        return None

    def getHstSrv(self, texturl):
        self.texturl = texturl
        service = re.search('(?<=service_name=)[\w-]+', texturl)
        if service is not None:
            service = service.group(0)
        else:
            service = re.search("(?<=/).+", self.texturl)
            if service is not None:
                service = service.group(0)
            else:
                service = None

        listhost = ""
        hosts = re.findall("(?<=host=)[\w-]+", self.texturl)

        if len(hosts) > 0:
            for host in hosts:
                listhost += "{} ".format(str(host))
        else:
            simple = re.search("(?<=@)[\w-]+", self.texturl)
            if simple is not None:
                listhost = simple.group(0)
            else:
                listhost = None

        return service, listhost

    def extractDsJb6(self):

        conurl = None
        ds_user = None
        ds_password = None
        seDomains = self.seDomains
        for datasource in self.sub_ds:
            ds_secdom = None

            for key, value in datasource.items():
                if key == "jndi-name":
                    jndi = value
            # catch connection-url
            for child in datasource:
                if child.tag == "{urn:jboss:domain:datasources:1.1}connection-url":
                    conurl = re.sub('[\s+]', '', child.text.strip().replace('\n', '</br>'))
            service, hosts = self.getHstSrv(conurl)

            # Catch user and password
            # if security-domain exist search inside for user and password
            # seDomains.findall(".//*[@name='RecaudacionDatabaseSecurity']")
            #
            for child in datasource:
                if child.tag == "{urn:jboss:domain:datasources:1.1}security":
                    for elsecurity in child:
                        if (elsecurity.tag ==
                                "{urn:jboss:domain:datasources:1.1}user-name"):
                            ds_user = elsecurity.text
                        if (elsecurity.tag ==
                                "{urn:jboss:domain:datasources:1.1}password"):
                            ds_password = elsecurity.text
                        if (elsecurity.tag ==
                                "{urn:jboss:domain:datasources:1.1}security-domain"):
                            ds_secdom = elsecurity.text
                            secdoms = seDomains.findall(".//*[@name='{}']"
                                                        .format(elsecurity.text))
                            secdom = secdoms[0].find(".//*[@name='userName']")
                            for key, value in secdom.items():
                                ds_user = value
                            secdom = secdoms[0].find(".//*[@name='password']")
                            for key, value in secdom.items():
                                ds_password = value
            jbossDataDic = {"jndi-name": jndi,
                            "connection-url": conurl,
                            "service-name": service,
                            "hosts": hosts,
                            "security-domain": ds_secdom,
                            "user-name": ds_user,
                            "password": ds_password}
            self.dictds.append(jbossDataDic)
        return self.dictds

    def extractDeployments(self):
        existdeploy = False
        for child in self.jbossxml:
            if child.tag == '{urn:jboss:domain:1.5}deployments':
                self.deployments = child
                existdeploy = True
        if existdeploy:
            for child in self.deployments:
                self.dicdeploy.append(child.attrib)
        return self.dicdeploy
