package xray

import (
	"context"
	"testing"

	"github.com/xtls/xray-core/app/proxyman/command"
	"github.com/xtls/xray-core/proxy/shadowsocks"
	"github.com/xtls/xray-core/proxy/shadowsocks_2022"
	"google.golang.org/grpc"
)

type captureShadowsocksClient struct {
	command.HandlerServiceClient
	request *command.AlterInboundRequest
}

func (c *captureShadowsocksClient) AlterInbound(_ context.Context, r *command.AlterInboundRequest, _ ...grpc.CallOption) (*command.AlterInboundResponse, error) {
	c.request = r
	return &command.AlterInboundResponse{}, nil
}

func TestAddUserShadowsocksAccountCompatibility(t *testing.T) {
	for _, tc := range []struct {
		cipher string
		want   shadowsocks.CipherType
	}{
		{"aes-128-gcm", shadowsocks.CipherType_AES_128_GCM},
		{"aes-256-gcm", shadowsocks.CipherType_AES_256_GCM},
		{"chacha20-poly1305", shadowsocks.CipherType_CHACHA20_POLY1305},
		{"chacha20-ietf-poly1305", shadowsocks.CipherType_CHACHA20_POLY1305},
		{"xchacha20-poly1305", shadowsocks.CipherType_XCHACHA20_POLY1305},
		{"xchacha20-ietf-poly1305", shadowsocks.CipherType_XCHACHA20_POLY1305},
		{"2022-blake3-aes-128-gcm", shadowsocks.CipherType_UNKNOWN},
		{"2022-blake3-aes-256-gcm", shadowsocks.CipherType_UNKNOWN},
		{"2022-blake3-chacha20-poly1305", shadowsocks.CipherType_UNKNOWN},
	} {
		t.Run(tc.cipher, func(t *testing.T) {
			c := &captureShadowsocksClient{}
			var client command.HandlerServiceClient = c
			api := XrayAPI{HandlerServiceClient: &client}
			if err := api.AddUser("shadowsocks", "fixture", map[string]any{"cipher": tc.cipher, "password": "test-only-key", "email": "test@example.invalid"}); err != nil {
				t.Fatal(err)
			}
			if c.request == nil || c.request.Tag != "fixture" {
				t.Fatal("missing request")
			}
			msg, err := c.request.Operation.GetInstance()
			if err != nil {
				t.Fatal(err)
			}
			op := msg.(*command.AddUserOperation)
			if op.User.Email != "test@example.invalid" {
				t.Fatal("email changed")
			}
			account, err := op.User.Account.GetInstance()
			if err != nil {
				t.Fatal(err)
			}
			if tc.want == shadowsocks.CipherType_UNKNOWN {
				got, ok := account.(*shadowsocks_2022.ServerConfig)
				if !ok || got.Key != "test-only-key" || got.Email != op.User.Email {
					t.Fatalf("bad 2022 account: %v", account)
				}
			} else {
				got, ok := account.(*shadowsocks.Account)
				if !ok || got.CipherType != tc.want || got.Password != "test-only-key" {
					t.Fatalf("bad AEAD account: %v", account)
				}
			}
		})
	}
}
