# coding:utf-8

from CCPRestSDK import REST
import ConfigParser

#主帐号
accountSid= '8aaf0708701429c001701a50a3520396';

#主帐号Token
accountToken= '04009be98c29438d8953419231cb7c4e';

#应用Id
appId='8aaf0708701429c001701a50a3af039c';

#请求地址，格式如下，不需要写http://
serverIP='sandboxapp.cloopen.com';

#请求端口 
serverPort='8883';

#REST版本号
softVersion='2013-12-26';

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id

class _CCP(object):
    """初始化REST SDK"""
    def __init__(self):
	    self.rest = REST(serverIP,serverPort,softVersion)
	    self.rest.setAccount(accountSid,accountToken)
	    self.rest.setAppId(appId)

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
	    cls._instance = cls()
	return cls._instance

    def sendTemplateSMS(self, to, datas, tempId):
	return self.rest.sendTemplateSMS(to, datas, tempId)


ccp = _CCP.instance()


if __name__ == '__main__':
    ccp.sendTemplateSMS()
