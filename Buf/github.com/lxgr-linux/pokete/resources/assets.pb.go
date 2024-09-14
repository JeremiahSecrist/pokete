// DO NOT EDIT!
// This code was auto generated by the `protoc-gen-pokete-resources` plugin,
// part of the pokete project, by <lxgr@protonmail.com>

package resources

type BaseAssets struct {
	Items        map[string]Item        `json:"items"`
	Pokes        map[string]Poke        `json:"pokes"`
	Attacks      map[string]Attack      `json:"attacks"`
	Natures      map[string]Nature      `json:"natures"`
	Weathers     map[string]Weather     `json:"weathers"`
	Types        map[string]Type        `json:"types"`
	SubTypes     []string               `json:"sub_types"`
	Achievements map[string]Achievement `json:"achievements"`
}

type MapTrainers struct {
	Trainers []Trainer `json:"trainers"`
}

type Assets struct {
	Trainers    map[string]MapTrainers `json:"trainers"`
	Npcs        map[string]NPC         `json:"npcs"`
	Obmaps      map[string]Obmap       `json:"obmaps"`
	Stations    map[string]Station     `json:"stations"`
	Decorations map[string]Decoration  `json:"decorations"`
	Maps        map[string]Map         `json:"maps"`
}
