protoc Message2Clients.proto --cpp_out=.
protoc MessageType.proto --cpp_out=.
protoc Message2Server.proto --cpp_out=.
protoc Services.proto --grpc_out=. --plugin=protoc-gen-grpc=`which grpc_cpp_plugin`
protoc Services.proto --cpp_out=.
mv -f ./*.h ../cpp/proto
mv -f ./*.cc ../cpp/proto
