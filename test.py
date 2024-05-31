import ldap

AUTH_LDAP_SERVER_URI = "ldap://10.101.64.41:389"  # ldap主机
AUTH_LDAP_BIND_DN = "CN=恒大宝,OU=应用系统账号,DC=hdjt,DC=hdad,DC=local"    # 根据自己实际需求填写
AUTH_LDAP_BIND_PASSWORD = "1qaz@WSX"   # 管理账户密码
SEARCH_BASE = "OU=恒大集团,DC=hdjt,DC=hdad,DC=local"


def ldap_auth(username, password):
    try:
        # 建立连接
        ldapconn = ldap.initialize(AUTH_LDAP_SERVER_URI)
        # 绑定管理账户，用于用户的认证
        ldapconn.simple_bind_s(AUTH_LDAP_BIND_DN, AUTH_LDAP_BIND_PASSWORD)
        search_scope = ldap.SCOPE_SUBTREE  # 指定搜索范围
        ATTRLIST = ['title']
        ATTRLIST = None
        search_filter = "(sAMAccountName=%s)" % username    # 指定搜索字段
        search_filter = "(departmentNumber=D0095744)"
        # search_filter = "(OU=房车宝集团技术开发中心后台开发组)"
        ldap_result = ldapconn.search_s(SEARCH_BASE, search_scope, search_filter, ATTRLIST)  # 返回该用户的所有信息，类型列表
        from pprint import pprint
        user_list = [{x[1]['sAMAccountName'][0].decode(): x[1]['cn'][0].decode()}
                     for x in ldap_result if isinstance(x[1], dict) and x[1].get('sAMAccountName')]
        print(len(user_list), user_list)
        ret_lst = []
        for x in ldap_result:
            x_lst = {}
            for k, v in x[1].items():
                v_lst = []
                for z in v:
                    try:
                        v_lst.append(z.decode())
                    except:
                        v_lst.append(z)
                x_lst[k] = v_lst
            ret_lst.append([x[0], x_lst])

        pprint(ret_lst)
        if ldap_result:
            user_dn = ldap_result[0][0]   # 获取用户的cn,ou,dc
            print(11111111, user_dn)
            try:
                is_number = ldapconn.compare_s(user_dn, 'cn', '李成波'.encode())
                print(222222222, is_number)
                ldapconn.simple_bind_s(user_dn, password)  # 对用户的密码进行验证
                print("验证成功")
                return True
            except ldap.LDAPError as e:
                print(22222222, e)
                return False
        else:
            return False
    except ldap.LDAPError as e:
        print(e)
        return False

    # r = ldapconn.simple_bind_s(ldap_result[0]["distinguishedName"][0].decode("utf-8"), password)  # 验证用户的账号和密码
    # print(r)
    # if ldap_result:
    #     print(ldap_result)
    #     result_data = ldapconn.result(ldap_result, 1)   # 获取需要认证用户的dn
    #     print(result_data)
        # if len(result_data):
        #     _, r_b = result_data[0]
        #     r = ldapconn.simple_bind_s(r_b["distinguishedName"][0].decode("utf-8"), password)  # 验证用户的账号和密码
        #     print(r)
    # else:
    #     return False


if __name__ == '__main__':
    ldap_auth('042834150', 'Liber314235')
