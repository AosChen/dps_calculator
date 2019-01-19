#!/usr/bin/python
# -*- coding: UTF-8 -*-

import yaml
class Target:
    def __init__(self,type):
        with open("./dataset.yml") as f:
            config = yaml.load(f.read())
        self.level = config['Target'][type][0]
        self.defense = config['Target'][type][1]
        self.hit_probability = config['Target'][type][2]
        self.unrivaled = config['Target'][type][3]
    
    def damage_reduce(self,defense_ignore):
        return 1 - self.defense*(1-defense_ignore)/(self.defense*(1-defense_ignore)+(4.084*(self.level*185-16800)))

    def hit_table(self,hit_probability,Crit_probability,unrivaled):
        miss    = max((self.hit_probability-hit_probability)/100,0)
        rivaled = max((self.unrivaled-unrivaled)/100,0)        
        crit    = min(Crit_probability,1-miss-rivaled)
        hit     = max(0,(1-miss-rivaled-crit))
        return miss,rivaled,hit,crit

class Role:
    def __init__(self,Base,Base_attack,Crit_probability,Crit_attack,
        defense_break,Hit_probability,Unrivaled,suit_attack,suit_skill):
        # 1700 5000 30 175 22 106 14 1 1
        self.base = Base
        self.base_attack = Base_attack
        self.crit_probability = Crit_probability/100
        self.crit_attack = Crit_attack/100
        self.defense_break = defense_break/100
        self.hit_probability = Hit_probability/100
        self.unrivaled = Unrivaled/100
        self.total_attack = self.base*1.95 + self.base_attack
        if suit_attack == 1:
            self.total_attack += self.base_attack*0.1
        self.Target = Target(1)
        with open("./dataset.yml") as f:
            self.config = yaml.load(f.read())

    def skill_KuaiXue(self):
        base_damage = self.total_attack*config["Ratio"]["yangming"]

        


if __name__ == "__main__":
    target = Target(2)
    print(target.hit_table(100,0.75,10))