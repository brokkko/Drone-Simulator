import React, { Component } from "react";
import Drone from "./Drone.js"

class DronesRenderer{
    constructor(scene) {
        this.drones = []
        this.scene = scene
    }

    fillDronesList(positions){
        for (let index in positions){
            this.drones.push(new Drone(positions[index]));
            this.scene.add(this.drones[index])
        }
    }


    updatePositions(coordinates){

        for (let i of coordinates){
            i.multiplyScalar(1/10)
        }

        if(this.drones.length === 0){
            this.fillDronesList(coordinates);
            return;
        }

        for(let index in coordinates){
            this.drones[index].position.copy(coordinates[index])
        }

    }
}

export default DronesRenderer

