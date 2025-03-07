package main

import (
	"bytes"
	"io"
	"net/http"
	"log"
	"github.com/gorilla/mux"
	"github.com/rs/cors"
)

const userServiceURL = "http://user_service:8000"

func proxyHandler(w http.ResponseWriter, r *http.Request) {
	targetURL := userServiceURL + r.URL.Path
	if r.URL.RawQuery != "" {
		targetURL += "?" + r.URL.RawQuery
	}

    body, err := io.ReadAll(r.Body)
    if err != nil {
        http.Error(w, "Error reading request body", http.StatusInternalServerError)
        return
    }
    defer r.Body.Close()

    proxyReq, err := http.NewRequest(r.Method, targetURL, bytes.NewReader(body))
    if err != nil {
        http.Error(w, "Error creating request", http.StatusInternalServerError)
        return
    }

    proxyReq.Header = r.Header

    resp, err := http.DefaultClient.Do(proxyReq)
    if err != nil {
        http.Error(w, "Error contacting user service", http.StatusInternalServerError)
        return
    }
    defer resp.Body.Close()

    w.WriteHeader(resp.StatusCode)
    io.Copy(w, resp.Body)
}

func main() {
	r := mux.NewRouter()
	r.HandleFunc("/register", proxyHandler).Methods("POST")
	r.HandleFunc("/login", proxyHandler).Methods("POST")
	r.HandleFunc("/profile", proxyHandler).Methods("GET", "PUT")

	handler := cors.AllowAll().Handler(r)

	log.Println("API Gateway running on port 8080")
	http.ListenAndServe(":8080", handler)
}
