// DO NOT EDIT!
// This code was auto generated by the `protoc-gen-pokete-resources` plugin,
// part of the pokete project, by <lxgr@protonmail.com>

package resources

import ()

type StationGen struct {
	Additionals []string `json:"additionals"`
	Desc        string   `json:"desc"`
	Text        string   `json:"text"`
	Color       string   `json:"color"`
	ANext       *string  `json:"a_next"`
	WNext       *string  `json:"w_next"`
	SNext       *string  `json:"s_next"`
	DNext       *string  `json:"d_next"`
}

type Station struct {
	Gen StationGen `json:"gen"`
	Add Coords     `json:"add"`
}

type DecorationGen struct {
	Text  string `json:"text"`
	Color string `json:"color"`
}

type Decoration struct {
	Gen DecorationGen `json:"gen"`
	Add Coords        `json:"add"`
}