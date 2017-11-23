package main

import (
	"crypto/sha1"
	"fmt"
	"io"
	"net/http"
	"sort"
)

func handle(responseWriter http.ResponseWriter, request *http.Request) {
	var signature, timestamp, nonce, echostr, token string

	token = ""
	request.ParseForm()
	rf := request.Form

	if v, ok := rf["signature"]; ok {
		signature = v[0]
	}

	if v, ok := rf["timestamp"]; ok {
		timestamp = v[0]
	}

	if v, ok := rf["nonce"]; ok {
		nonce = v[0]
	}

	if v, ok := rf["echostr"]; ok {
		echostr = v[0]
	}

	sArr := []string{token, timestamp, nonce}

	sort.Strings(sArr)

	str := sArr[0] + sArr[1] + sArr[2]

	t := sha1.New()
	io.WriteString(t, str)
	sha1 := fmt.Sprintf("%x", t.Sum(nil))

	if sha1 == signature {
		fmt.Fprintf(responseWriter, echostr)
		fmt.Printf("success deal a wechat register\n")
	} else {
		fmt.Printf("fail")
	}

	return
}

func main() {
	fmt.Printf("wait wechat request\n")
	http.HandleFunc("/wechat/token", handle)

	http.ListenAndServe(":80", nil)
}
