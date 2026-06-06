
export class SocketModel {
    constructor(namespace) {
        this.namespace = namespace;
        this.socket = null;
    }
    connect() {
        this.socket = io(`http://127.0.0.1:8000/${this.namespace}`);
        this.socket.on("connect", () => {
            console.log(`${this.namespace} connected Socket`);
        
        });
        this.socket.on("disconnect", () => {
            console.log(`${this.namespace} disconnected`);
        });
    }
    emit(event, data) {
        this.socket.emit(event, data);
    }
    on(event, callback) {
        this.socket.on(event, callback);
    }
}