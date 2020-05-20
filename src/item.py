#item.py
__author__ = "Fergus Griggs";
__email__ = "fbob987 at gmail dot com";

import random;

import tables;

def GetRandomItemPrefix(prefixCategory):
    return [prefixCategory, tables.prefixData[prefixCategory][random.randint(0, len(tables.prefixData[prefixCategory])-1)]];

class Item():
    def __init__(self, ID, amnt = 1, forceNoPrefix = False):
        self.name = str(tables.itemData[ID][0]);
        self.ID = ID;
        self.amnt = amnt;
        self.tags = list(tables.itemData[ID][1]);

        if tables.itemData[ID][3][0] != None: self.attackDamage = float(tables.itemData[ID][3][0]);
        if tables.itemData[ID][3][1] != None: self.attackSpeed = int(tables.itemData[ID][3][1]);
        if tables.itemData[ID][3][2] != None: self.critStrikeChance = float(tables.itemData[ID][3][2]);
        if tables.itemData[ID][3][3] != None: self.size = float(tables.itemData[ID][3][3]);
        if tables.itemData[ID][3][4] != None: self.velocity = float(tables.itemData[ID][3][4]);
        if tables.itemData[ID][3][5] != None: self.manaCost = float(tables.itemData[ID][3][5]);
        if tables.itemData[ID][3][6] != None: self.knockback = float(tables.itemData[ID][3][6]);
        if tables.itemData[ID][3][7] != None: self.tier = int(tables.itemData[ID][3][7]);

        self.description = str(tables.itemData[ID][4]);

        # 15% chance to be given a prefix if it has a prefix category and is not forced not to have one
        if len(tables.itemData[ID][2]) > 0 and not forceNoPrefix and random.random() > 0.15:
            self.hasPrefix = True;
            self.prefixData = GetRandomItemPrefix(tables.itemData[ID][2][random.randint(0, len(tables.itemData[ID][2]) - 1)]);

            if self.prefixData[0] == "universal":
                self.attackDamage *= (1 + self.prefixData[1][1]);
                self.critStrikeChance = max(min(1.0, self.critStrikeChance + self.prefixData[1][2]), -1.0);
                self.knockback *= (1 + self.prefixData[1][3]);
                self.tier += self.prefixData[1][4];

            elif self.prefixData[0] == "common":
                self.attackDamage *= (1 + self.prefixData[1][1]);
                self.attackSpeed *= (1 - self.prefixData[1][2]);
                self.critStrikeChance += max(min(1.0, self.critStrikeChance + self.prefixData[1][3]), -1.0);
                self.knockback *= (1 + self.prefixData[1][4]);
                self.tier += self.prefixData[1][5];

            elif self.prefixData[0] == "melee":
                self.attackDamage *= (1 + self.prefixData[1][1]);
                self.attackSpeed *= (1 - self.prefixData[1][2]);
                self.critStrikeChance += max(min(1.0, self.critStrikeChance + self.prefixData[1][3]), -1.0);
                self.size *= (1 + self.prefixData[1][4]);
                self.knockback *= (1 + self.prefixData[1][5]);
                self.tier += self.prefixData[1][6];

            elif self.prefixData[0] == "ranged":
                self.attackDamage *= (1 + self.prefixData[1][1]);
                self.attackSpeed *= (1 - self.prefixData[1][2]);
                self.critStrikeChance += max(min(1.0, self.critStrikeChance + self.prefixData[1][3]), -1.0);
                self.velocity *= (1 + self.prefixData[1][4]);
                self.knockback *= (1 + self.prefixData[1][5]);
                self.tier += self.prefixData[1][6];

            elif self.prefixData[0] == "magic":
                self.attackDamage *= (1 + self.prefixData[1][1]);
                self.attackSpeed *= (1 - self.prefixData[1][2]);
                self.critStrikeChance += max(min(1.0, self.critStrikeChance + self.prefixData[1][3]), 0);
                self.manaCost *= (1 + self.prefixData[1][4]);
                self.knockback *= (1 + self.prefixData[1][5]);
                self.tier += self.prefixData[1][6];
        else:
            self.prefixData = None;
            self.hasPrefix = False;

    def GetName(self):
        if self.hasPrefix:
            return self.prefixData[1][0] + " " + self.name;
        else:
            return self.name;