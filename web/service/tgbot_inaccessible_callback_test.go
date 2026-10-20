package service

import (
	"context"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/mymmrac/telego"
	th "github.com/mymmrac/telego/telegohandler"
)

func TestLegacyCallbackRejectsMissingOrInaccessibleMessage(t *testing.T) {
	for _, tc := range []struct {
		name    string
		message telego.MaybeInaccessibleMessage
	}{
		{name: "missing"},
		{name: "inaccessible", message: &telego.InaccessibleMessage{}},
		{name: "typed nil", message: (*telego.Message)(nil)},
	} {
		t.Run(tc.name, func(t *testing.T) {
			var methods []string
			srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				methods = append(methods, r.URL.Path)
				w.Header().Set("Content-Type", "application/json")
				io.WriteString(w, `{"ok":true,"result":true}`)
			}))
			defer srv.Close()
			notifier := &Tgbot{}
			localBot, err := notifier.NewBot(strings.Repeat("1", 9)+":"+strings.Repeat("a", 35), "", srv.URL)
			if err != nil {
				t.Fatal(err)
			}
			group := &th.HandlerGroup{}
			group.HandleCallbackQuery(notifier.handleCallbackQuery)
			query := &telego.CallbackQuery{ID: "inaccessible", Message: tc.message, Data: "restart_panel_confirm"}
			if err := group.HandleUpdate(context.Background(), localBot, telego.Update{CallbackQuery: query}); err != nil {
				t.Fatal(err)
			}
			if len(methods) != 1 || !strings.HasSuffix(methods[0], "/answerCallbackQuery") {
				t.Fatalf("expected callback answer only, got %v", methods)
			}
		})
	}
}
