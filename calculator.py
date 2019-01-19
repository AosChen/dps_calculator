#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
世外蓬莱花间dps计算器
version：1.0
author：Lan An
'''

class Target:
    def __init__(self,type):
        target_choice = [[102,2818,105,20],
                        [103,4959,110,30]]
        self.level = target_choice[type][0]
        self.defense = target_choice[type][1]
        self.hit_probability = target_choice[type][2]
        self.unrivaled = target_choice[type][3]
        print("目标等级",self.level)
    
    def damage_reduce(self,defense_ignore):
        '''
        计算boss减伤
        defense_ignore:
            无视防御比例
        return:
            boss受到伤害的比例
        '''
        return 1 - self.defense*(1-defense_ignore)/(self.defense*(1-defense_ignore)+(4.084*(self.level*185-16800)))

    def hit_table(self,hit_probability,Crit_probability,unrivaled):
        '''
        计算圆桌理论命中类型分布
        arg:
            hit_probability:命中率
            Crit_probability:会心
            unrivaled:无双
        return:
            miss:未命中概率
            rivaled:识破概率
            hit:普通命中概率
            crit:会心命中概率
        '''
        miss    = max((self.hit_probability/100-hit_probability),0)
        rivaled = max((self.unrivaled/100-unrivaled),0)        
        crit    = min(Crit_probability,1-miss-rivaled)
        hit     = max(0,(1-miss-rivaled-crit))
        return miss,rivaled,hit,crit

class Role:
    def __init__(self,Base,Base_attack,Crit_probability,Crit_attack,
        defense_break,Hit_probability,Unrivaled,suit_attack,suit_skill):
        '''
        arg:
            Base : 元气
            Base_attack : 基础攻击
            Crit_probability : 会心率,例如25%会心写25
            Crit_attack : 会心效果,例如175%会效写175
            defense_break : 破防,例如20%破防写20
            Hit_probability : 命中率,例如106%命中写106
            Unrivaled : 无双,例如20%无双写20
            suit_attack : 是否有10%攻击套装特效,1-有,0-无
            suit_skill : 是否有10%技能伤害特效,1-有,0-无
        '''
        self.base = Base
        self.base_attack = Base_attack
        self.crit_probability = Crit_probability/100
        self.crit_attack = Crit_attack/100
        self.defense_break = defense_break/100
        self.hit_probability = Hit_probability/100
        self.unrivaled = Unrivaled/100
        self.suit_attack = suit_attack
        self.suit_skill = suit_skill
        self.Target = Target(1)

    def changeTarget(self,target_type):
        '''修改测试目标'''
        self.Target = Target(target_type)

    def total_attack(self):
        '''获取总攻击力'''
        total_attack = self.base*1.95 + self.base_attack
        if self.suit_attack == 1:
            total_attack += self.base_attack*0.1
        return total_attack

    def shuiyue(self):
        '''开水月'''
        self.base_attack *= 1.3

    def chunhan(self):
        '''开春寒乱撒'''
        self.crit_probability += 0.2

    def end_shuiyue(self):
        '''水月结束'''
        self.base_attack /= 1.3

    def end_chunhan(self):
        '''春寒乱洒结束'''
        self.crit_probability -= 0.2

    def teamBuff(self):
        '''计算实战加成'''
        pass

    def skill_KuaiXue(self,num_dot):
        '''
        计算快雪单跳伤害
        num_dot:玉石吞噬dot跳数，即雪中行层数
        '''
        ratio = 0.42
        extra_crit = 0.25
        extra_crit_attack = 0.25
        damage_increase_miji = 0.12
        damage_increase_qixue = 0.44

        damage = self.total_attack()*ratio #基础伤害
        crit_probability = self.crit_probability
        crit_attack = self.crit_attack

        damage *= (1+damage_increase_miji)  #秘籍加成
        damage *= 1.1                       #噬骨

        #计算奇穴加成
        qixue_increase = damage_increase_qixue #奇穴加成
        qixue_increase += num_dot*0.1          #雪中行加成，10%每dot
        crit_probability += extra_crit         #额外会心
        crit_attack += extra_crit_attack       #额外会效
        damage *= (1+qixue_increase)

        #计算破防加成
        damage *= (1+self.defense_break)
        #计算套装效果
        if self.suit_skill == 1:
            damage *= 1.1
        #计算圆桌分布
        miss,rivaled,hit,crit = self.Target.hit_table(self.hit_probability,crit_probability,self.unrivaled)
        #计算期望伤害
        expectation_damage = damage*(miss*0+rivaled*0.25+hit*1+crit*crit_attack)
        #计算目标减伤
        return expectation_damage*self.Target.damage_reduce(defense_ignore=0.2)

    def skill_YangMing(self):
        '''
        计算阳明单次伤害
        '''
        ratio = 1.18
        extra_crit = 0.18
        extra_crit_attack = 0.15
        damage_increase_miji = 0.04
        damage_increase_qixue = 0
        crit_probability = self.crit_probability
        crit_attack = self.crit_attack

        damage = self.total_attack()*ratio  #基础伤害
        damage *= (1+damage_increase_miji)  #秘籍伤害加成
        damage *= (1+damage_increase_qixue) #奇穴伤害加成
        crit_probability += extra_crit      #额外会心
        crit_attack += extra_crit_attack    #额外会效
        damage *= 1.1                       #噬骨
        if self.suit_skill == 1:            #套装技能
            damage *= 1.1
        #计算破防加成
        damage *= (1+self.defense_break)
        #计算圆桌分布
        miss,rivaled,hit,crit = self.Target.hit_table(self.hit_probability,crit_probability,self.unrivaled)
        #计算期望伤害
        expectation_damage = damage*(miss*0+rivaled*0.25+hit*1+crit*crit_attack)
        #计算目标减伤
        return expectation_damage*self.Target.damage_reduce(defense_ignore=0.2)

    def skill_other(self,skill):
        '''
        计算其他几个技能伤害
        skill:技能名
        '''
        ratio = {
            "shangyang": 0.33,     #商阳第一跳
            "shangyang_dot": 0.29, #商阳DOT
            "lancui_dot": 0.34,    #兰摧DOT
            "zhonglin_dot": 0.31,  #钟林DOT
            "tage": 0.2,           #踏歌触发
            "xuezhongxing": 1.07,  #雪中行附加  
            "yushi": 0.33          #玉石俱焚
        }
        crit_probability = self.crit_probability
        crit_attack = self.crit_attack
        damage = self.total_attack()*ratio[skill]   #基础伤害
        damage *= 1.1                               #噬骨
        #计算破防加成
        damage *= (1+self.defense_break)
        #计算圆桌分布
        miss,rivaled,hit,crit = self.Target.hit_table(self.hit_probability,crit_probability,self.unrivaled)
        #计算期望伤害
        expectation_damage = damage*(miss*0+rivaled*0.25+hit*1+crit*crit_attack)
        #计算目标减伤
        return expectation_damage*self.Target.damage_reduce(defense_ignore=0.2)
    def calculator_dps(self):
        '''
        春寒流离61s循环计算dps
        '''
        accumulative_damage = 0
        #起手3dot
        accumulative_damage += self.skill_other("shangyang")
        accumulative_damage += self.skill_other("shangyang_dot")*7
        accumulative_damage += self.skill_other("lancui_dot")*7
        accumulative_damage += self.skill_other("zhonglin_dot")*7
        #玉石
        accumulative_damage += self.skill_other("yushi")

        '''水月乱洒'''
        self.shuiyue()
        self.chunhan()
        #补3dot，触发雪中行伤害
        accumulative_damage += self.skill_other("shangyang")
        accumulative_damage += self.skill_other("shangyang_dot")*7
        accumulative_damage += self.skill_other("lancui_dot")*7
        accumulative_damage += self.skill_other("zhonglin_dot")*7
        accumulative_damage += self.skill_other("xuezhongxing")*3
        #快雪×5，吞噬21dot
        accumulative_damage += self.skill_KuaiXue(21)*5
        #玉石
        accumulative_damage += self.skill_other("yushi")

        #阳明+商阳，触发雪中行伤害
        accumulative_damage += self.skill_YangMing()
        accumulative_damage += self.skill_other("lancui_dot")*7
        accumulative_damage += self.skill_other("zhonglin_dot")*7
        accumulative_damage += self.skill_other("shangyang")
        accumulative_damage += self.skill_other("shangyang_dot")*7
        accumulative_damage += self.skill_other("xuezhongxing")*1
        #爆发阶段触发踏歌平均6次(5*0.4*3)
        accumulative_damage += self.skill_other("tage")*1
        self.end_shuiyue()
        self.end_chunhan()
        '''水月乱洒结束'''

        #快雪×5，吞噬17dot
        accumulative_damage += self.skill_KuaiXue(17)*5
        #快雪×7，无雪中行加成
        accumulative_damage += self.skill_KuaiXue(0)*7
        #玉石
        accumulative_damage += self.skill_other("yushi")

        #三次普通循环
        for i in range(3):
            #补3dot，触发雪中行伤害
            accumulative_damage += self.skill_other("shangyang")
            accumulative_damage += self.skill_other("shangyang_dot")*7
            accumulative_damage += self.skill_other("lancui_dot")*7
            accumulative_damage += self.skill_other("zhonglin_dot")*7
            accumulative_damage += self.skill_other("xuezhongxing")*3
            #快雪×5，吞噬11dot
            accumulative_damage += self.skill_KuaiXue(11)*5
            #快雪×7，无雪中行加成
            accumulative_damage += self.skill_KuaiXue(0)*7
            #玉石
            accumulative_damage += self.skill_other("yushi")
        #非爆发阶段触发踏歌平均(48*0.4*3)平均次
        accumulative_damage += self.skill_other("tage")*48*0.4*3
        return (accumulative_damage/61)
    def report(self):
        '''
        生成属性收益报告
        '''
        result = ''
        base = self.calculator_dps()
        self.base += 1
        result += "元气收益："+str(self.calculator_dps()-base)+'\n'
        self.base -= 1

        self.base_attack += 1
        result += "攻击收益："+str(self.calculator_dps()-base)+'\n'
        self.base_attack -= 1

        self.crit_probability += 0.01
        result += "会心收益："+str((self.calculator_dps()-base)/153.442)+'\n'
        self.crit_probability -= 0.01

        self.crit_attack += 0.01
        result += "会效收益："+str((self.calculator_dps()-base)/53.703)+'\n'
        self.crit_attack -= 0.01

        self.defense_break += 0.01
        result += "破防收益："+str((self.calculator_dps()-base)/153.442)+'\n'
        self.defense_break -= 0.01

        self.unrivaled += 0.01
        result += "无双收益："+str((self.calculator_dps()-base)/87.176)+'\n'
        self.unrivaled -= 0.01

        self.hit_probability += 0.01
        result += "命中收益："+str((self.calculator_dps()-base)/139.485)+'\n'
        self.hit_probability -= 0.01

        return result

if __name__ == "__main__":  
    base = 1822
    base_attack = 5674
    crit = 0
    crit_attack = 175
    defense_break = 50
    hit_probability = 105.77
    unrivaled = 18.24
    has_suit_2 = 1
    has_suit_4 = 0
    role = Role(base,base_attack,crit,crit_attack,defense_break,
    hit_probability,unrivaled,has_suit_4,has_suit_2)
    print("DPS:",role.calculator_dps())
    print(role.report())
    print("会心   破防   dps")
    while(1):
        role.crit_probability += 0.01
        role.defense_break -= 0.01
        print(role.crit_probability,role.defense_break,role.calculator_dps())
        if role.defense_break <= 0:
            break