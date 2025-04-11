package main

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/gorilla/mux"
	"github.com/rs/cors"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	postpb "github.com/network/src/gateway_service/post/proto"
)

const (
    userServiceURL = "http://user_service:8000"
    grpcPostAddr   = "post_service:50051"
)

func grpcCodeToHTTP(code codes.Code) int {
    switch code {
    case codes.OK:
        return http.StatusOK
    case codes.NotFound:
        return http.StatusNotFound
    case codes.PermissionDenied:
        return http.StatusForbidden
    case codes.Unauthenticated:
        return http.StatusUnauthorized
    case codes.InvalidArgument:
        return http.StatusBadRequest
    default:
        return http.StatusInternalServerError
    }
}

func proxyHandler(w http.ResponseWriter, r *http.Request) {
	targetURL := userServiceURL + r.URL.Path
	if r.URL.RawQuery != "" {
		targetURL += "?" + r.URL.RawQuery
	}

    body, err := io.ReadAll(r.Body)
    if err != nil {
        st, _ := status.FromError(err);
        http.Error(w, err.Error(), grpcCodeToHTTP(st.Code()))
        return
    }
    defer r.Body.Close()

    proxyReq, err := http.NewRequest(r.Method, targetURL, bytes.NewReader(body))
    if err != nil {
        st, _ := status.FromError(err);
        http.Error(w, err.Error(), grpcCodeToHTTP(st.Code()))
        return
    }

    proxyReq.Header = r.Header

    resp, err := http.DefaultClient.Do(proxyReq)
    if err != nil {
        st, _ := status.FromError(err);
        http.Error(w, err.Error(), grpcCodeToHTTP(st.Code()))
        return
    }
    defer resp.Body.Close()

    w.WriteHeader(resp.StatusCode)
    io.Copy(w, resp.Body)
}

var postClient postpb.PostServiceClient

func createPostHandler(w http.ResponseWriter, r *http.Request) {
    var reqBody struct {
        Title       string   `json:"title"`
        Description string   `json:"description"`
        CreatorID   string   `json:"creator_id"`
        IsPrivate   bool     `json:"is_private"`
        Tags        []string `json:"tags"`
    }

    if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
        http.Error(w, "Invalid request body", http.StatusBadRequest)
        return
    }

    grpcReq := &postpb.CreatePostRequest{
        Title:       reqBody.Title,
        Description: reqBody.Description,
        CreatorId:   reqBody.CreatorID,
        IsPrivate:   reqBody.IsPrivate,
        Tags:        reqBody.Tags,
    }

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    grpcResp, err := postClient.CreatePost(ctx, grpcReq)
    if err != nil {
        st, _ := status.FromError(err);
        http.Error(w, st.Message(), grpcCodeToHTTP(st.Code()))
        return
    }

    json.NewEncoder(w).Encode(grpcResp.Post)
}

func getPostHandler(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    postID := vars["id"]
    requesterID := r.URL.Query().Get("requester_id")

    grpcReq := &postpb.GetPostRequest{
        PostId:      postID,
        RequesterId: requesterID,
    }

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    grpcResp, err := postClient.GetPost(ctx, grpcReq)
    if err != nil {
        st, _ := status.FromError(err);
        http.Error(w, st.Message(), grpcCodeToHTTP(st.Code()))
        return
    }

    json.NewEncoder(w).Encode(grpcResp.Post)
}

func updatePostHandler(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    postID := vars["id"]

    var reqBody struct {
        Title       string   `json:"title"`
        Description string   `json:"description"`
        IsPrivate   bool     `json:"is_private"`
        Tags        []string `json:"tags"`
        RequesterID string   `json:"requester_id"`
    }

    if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
        http.Error(w, "Invalid request body", http.StatusBadRequest)
        return
    }

    grpcReq := &postpb.UpdatePostRequest{
        PostId:      postID,
        Title:       reqBody.Title,
        Description: reqBody.Description,
        IsPrivate:   reqBody.IsPrivate,
        Tags:        reqBody.Tags,
        RequesterId: reqBody.RequesterID,
    }

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    grpcResp, err := postClient.UpdatePost(ctx, grpcReq)
    if err != nil {
        st, _ := status.FromError(err);
        http.Error(w, st.Message(), grpcCodeToHTTP(st.Code()))
        return
    }

    json.NewEncoder(w).Encode(grpcResp.Post)
}

func deletePostHandler(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    postID := vars["id"]
    requesterID := r.URL.Query().Get("requester_id")

    grpcReq := &postpb.DeletePostRequest{
        PostId:      postID,
        RequesterId: requesterID,
    }

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    _, err := postClient.DeletePost(ctx, grpcReq)
    if err != nil {
        st, _ := status.FromError(err);
        http.Error(w, st.Message(), grpcCodeToHTTP(st.Code()))
        return
    }

    w.WriteHeader(http.StatusNoContent)
}

func listPostsHandler(w http.ResponseWriter, r *http.Request) {
    var page int32 = 1
    var pageSize int32 = 10
    requesterID := r.URL.Query().Get("requester_id")

    if p := r.URL.Query().Get("page"); p != "" {
        if parsed, err := strconv.Atoi(p); err == nil {
            page = int32(parsed)
        }
    }
    if ps := r.URL.Query().Get("page_size"); ps != "" {
        if parsed, err := strconv.Atoi(ps); err == nil {
            pageSize = int32(parsed)
        }
    }

    grpcReq := &postpb.ListPostsRequest{
        Page:        page,
        PageSize:    pageSize,
        RequesterId: requesterID,
    }

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    grpcResp, err := postClient.ListPosts(ctx, grpcReq)
    if err != nil {
        st, _ := status.FromError(err);
        http.Error(w, st.Message(), grpcCodeToHTTP(st.Code()))
        return
    }

    json.NewEncoder(w).Encode(grpcResp)
}

func main() {
    conn, err := grpc.Dial(grpcPostAddr, grpc.WithInsecure())
    if err != nil {
        log.Fatalf("failed to connect to post service: %v", err)
    }
    defer conn.Close()
    postClient = postpb.NewPostServiceClient(conn)

    r := mux.NewRouter()

    r.HandleFunc("/register", proxyHandler).Methods("POST")
    r.HandleFunc("/login", proxyHandler).Methods("POST")
    r.HandleFunc("/profile", proxyHandler).Methods("GET", "PUT")
    r.HandleFunc("/posts", createPostHandler).Methods("POST")
    r.HandleFunc("/posts", listPostsHandler).Methods("GET")
    r.HandleFunc("/posts/{id}", getPostHandler).Methods("GET")
    r.HandleFunc("/posts/{id}", updatePostHandler).Methods("PUT")
    r.HandleFunc("/posts/{id}", deletePostHandler).Methods("DELETE")

    handler := cors.AllowAll().Handler(r)

    log.Println("API Gateway running on port 8080")
    if err := http.ListenAndServe(":8080", handler); err != nil {
        log.Fatalf("failed to start server: %v", err)
    }
}
