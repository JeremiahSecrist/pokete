// DO NOT EDIT!
// This code was auto generated by the `protoc-gen-pokete-resources` plugin,
// part of the pokete project, by <lxgr@protonmail.com>

package base

import ()

type BaseIco struct {
	Txt string   `json:"txt"`
	Esc []string `json:"esc"`
}

type Poke struct {
	Name        string    `json:"name"`
	Hp          uint32    `json:"hp"`
	Atc         uint32    `json:"atc"`
	Defense     uint32    `json:"defense"`
	Attacks     []string  `json:"attacks"`
	Pool        []string  `json:"pool"`
	MissChance  float32   `json:"miss_chance"`
	Desc        string    `json:"desc"`
	LoseXp      uint32    `json:"lose_xp"`
	Rarity      float32   `json:"rarity"`
	Types       []string  `json:"types"`
	EvolvePoke  string    `json:"evolve_poke"`
	EvolveLvl   uint32    `json:"evolve_lvl"`
	Initiative  uint32    `json:"initiative"`
	NightActive *bool     `json:"night_active"`
	Ico         []BaseIco `json:"ico"`
}