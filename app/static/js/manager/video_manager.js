export class VideoManager {
    constructor(videoElement) {
        this.video = videoElement;
        this.ws = null;
    }
    connect() {
        this.ws = new WebSocket(
            "ws://127.0.0.1:8000/captureproduct/ws"
        );
        this.ws.binaryType = "arraybuffer";
        this.ws.onmessage = (event) => {
            const blob = new Blob(
                [event.data],
                { type: "image/jpeg" }
            );
            this.video.src =
                URL.createObjectURL(blob);
        };
    }
}