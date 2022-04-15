import * as THREE from "three";

class Drone extends THREE.Mesh{
    constructor(pos) {

        let radius = 0.5;
        let widthSegments = 32;
        let heightSegments = 16;
        let color = 0xffff00;
        let geometry = new THREE.SphereGeometry(radius, widthSegments, heightSegments);
        let material = new THREE.MeshBasicMaterial({color: color} );

        super(geometry, material)
        this.position.copy(pos)

        this.colorDisconnected = 0x4D4D4D
        this.colorConnected = 0x00ff00;

    }

    setColor = (status) => {
        +status ? this.material.color.setHex(this.colorConnected) : this.material.color.setHex(this.colorDisconnected)
    }

}

export default Drone

