#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from love_home.libs.yunsms.CCPRestSDK import REST
import ConfigParser

#���ʺ�
accountSid= '8a216da8627648690162854c969205ad'

#���ʺ�Token
accountToken= '446e7f4dc7a84776b420459763927a33'

#Ӧ��Id
appId='8a216da8627648690162854c96f305b4'

#�����ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com'

#����˿� 
serverPort='8883'

#REST�汾��
softVersion='2013-12-26'

  # ����ģ�����
  # @param to �ֻ�����
  # @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
  # @param $tempId ģ��Id

def sendTemplateSMS(to,datas,tempId):

    
    #��ʼ��REST SDK
    rest = REST(serverIP,serverPort,softVersion)
    rest.setAccount(accountSid,accountToken)
    rest.setAppId(appId)
    
    result = rest.sendTemplateSMS(to,datas,tempId)
    for k,v in result.iteritems(): 
        
        if k=='templateSMS' :
                for k,s in v.iteritems(): 
                    print '%s:%s' % (k, s)
        else:
            print '%s:%s' % (k, v)
    return result

