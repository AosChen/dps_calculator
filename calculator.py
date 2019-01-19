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
        miss    = max((self.hit_probability-hit_probability)/100,0)
        rivaled = max((self.unrivaled-unrivaled)/100,0)        
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
        self.total_attack = self.base*1.95 + self.base_attack
        self.suit_attack = suit_attack
        self.suit_skill = suit_skill
        if suit_attack == 1:
            self.total_attack += self.base_attack*0.1
        self.Target = Target(1)

    def shuiyue(self):
        '''
        开水月
        '''
        self.base_attack *= 1.3
        self.total_attack = self.base*1.95 + self.base_attack

    def chunhan(self):
        '''
        开春寒乱撒
        '''
        self.crit_probability += 0.2

    def teamBuff(self):
        '''
        计算实战加成
        '''
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

        damage = self.total_attack*ratio #基础伤害
        crit_probability = self.crit_probability
        crit_attack = self.crit_attack

        damage *= (1+damage_increase_miji)  #秘籍加成
        damage *= 1.1                       #噬骨

        #计算奇穴加成
        qixue_increase = damage_increase_qixue #奇穴加成
        qixue_increase += num_dot*0.1          #雪中行加成，10%每dot
        crit_probability += extra_crit         #额外会心
        crit_attack += extra_crit_attack       #额外会效
        damage *= qixue_increase

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

        damage = self.total_attack*ratio    #基础伤害
        damage *= (1+damage_increase_miji)  #秘籍伤害加成
        damage *= (1+damage_increase_qixue) #奇穴伤害加成
        crit_probability += extra_crit      #额外会心
        crit_attack += extra_crit_attack    #额外会效
        damage *= 1.1                       #噬骨
        if self.suit_skill == 1:            #套装技能
            damage *= 1.1

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
        damage = self.total_attack*ratio[skill]     #基础伤害
        damage *= 1.1                               #噬骨
        #计算圆桌分布
        miss,rivaled,hit,crit = self.Target.hit_table(self.hit_probability,crit_probability,self.unrivaled)
        #计算期望伤害
        expectation_damage = damage*(miss*0+rivaled*0.25+hit*1+crit*crit_attack)
        #计算目标减伤
        return expectation_damage*self.Target.damage_reduce(defense_ignore=0.2)

if __name__ == "__main__":  
    role = Role(1822,5674,10.47,175,40.99,106,18.24,0,1)
    print(role.skill_KuaiXue(0))