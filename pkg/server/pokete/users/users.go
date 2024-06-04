package users

import (
    "errors"
    "github.com/lxgr-linux/pokete/server/pokete/positions"
    "github.com/lxgr-linux/pokete/server/pokete/user"
)

var (
    USER_PRESENT error = errors.New("newUser already present")
)

type Users struct {
    users     *map[uint64]user.User
    positions *positions.Positions
}

func (u Users) Add(conId uint64, newUser user.User) error {
    for _, us := range *u.users {
        if us.Name == newUser.Name {
            return USER_PRESENT
        }
    }

    (*u.users)[conId] = newUser
    err := u.positions.BroadcastChange(conId, newUser)

    return err
}

func (u Users) Remove(conId uint64) {
    delete(*u.users, conId)
}

func (u Users) GetAllUsers() (retUsers []user.User) {
    for _, us := range *u.users {
        retUsers = append(retUsers, us)
    }
    return
}

func (u Users) GetAllUserNames() (names []string) {
    for _, us := range *u.users {
        names = append(names, us.Name)
    }
    return
}

func (u Users) SetNewPositionToUser(conId uint64, newPosition user.Position) error {
    us := (*u.users)[conId]
    err := us.Position.Change(newPosition)
    (*u.users)[conId] = us
    err = u.positions.BroadcastChange(conId, us)
    return err
}

func NewUsers(positions2 *positions.Positions) *Users {
    var tempUsers = make(map[uint64]user.User)
    return &Users{
        users:     &tempUsers,
        positions: positions2,
    }
}