import * as THREE from "three";

class Drone extends THREE.Mesh{
    constructor(pos) {
        let radius = 0.5/4
        let widthSegments = 32;
        let heightSegments = 16;
        let color = 0xffff00;
        let geometry = new THREE.SphereGeometry(radius, widthSegments, heightSegments);
        let material = new THREE.MeshBasicMaterial({color: color} );

        super(geometry, material)
        this.position.copy(pos)

        this.colorDisconnected =0x4D4D4D;
        this.colorConnected = 0x00ff00;
        this.colorReached = 0xff0000;

    }

    setColor = (status) => {
        status = +status
        if (status === 0){
            this.material.color.setHex(this.colorDisconnected)
        }
        else if (status === 1){
            this.material.color.setHex(this.colorConnected)
        }
        else if (status === 2){
            this.material.color.setHex(this.colorReached)
        }

    }

}

export default Drone

