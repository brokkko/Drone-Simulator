import React, { Component } from "react";
import * as THREE from "three";
import {OrbitControls} from "three/examples/jsm/controls/OrbitControls";

import DronesRenderer from "./DronesRenderer";
import parseData from "./ParseData";


class Scene extends Component {
    constructor(props) {
        super(props);
        this.init();
        this.socket = props.Socket
        this.socket.onmessage = this.socketOnMessage
        this.keyboardState = '0'
        this.controls = new OrbitControls(this.camera, this.renderer.domElement)
        this.controls.enableDamping = true
        this.controls.maxPolarAngle = Math.PI/2
        this.controls.minPolarAngle = 0
        this.controls.update()

        this.dronesRenderer = new DronesRenderer(this.scene)


        this.startAnimation()
        // document.onkeydown = this.onKeyPressed
        // document.onkeyup = this.onKeyReleased

    }

    // onKeyPressed = (e) => {
    //     if(e.key === 'w' || e.key === 'a' || e.key === 's' || e.key === 'd' || e.key === 'q')
    //         this.keyboardState = e.key;
    // }
    //
    // onKeyReleased = (e) => {
    //     this.keyboardState = '0';
    // }

    socketOnMessage = (event) =>{
        let positions = parseData(event.data)
        this.dronesRenderer.updatePositions(positions)
        this.socket.send(this.keyboardState)
    }

    startAnimation = () =>{

        if(this.animationID){
            window.cancelAnimationFrame(this.animationID)
        }

        let scene = this.scene
        let camera = this.camera
        let renderer = this.renderer
        let controls = this.controls

        function tick() {
            // chair.animate()
            renderer.render( scene, camera );
            controls.update()



            window.requestAnimationFrame(tick)

        }

        this.animationID = window.requestAnimationFrame(tick)
    }

    initLights = () => {
        const skyColor = 0xB1E1FF;  // light blue
        const groundColor = 0xB97A20;  // brownish orange
        const intensity = 0.3;
        let light = new THREE.HemisphereLight(skyColor, groundColor, intensity);
        this.scene.add(light);
        let pointLight = new THREE.PointLight(0xffffff, 2)
        pointLight.position.x = 3
        pointLight.position.y = 10
        pointLight.position.z = 0
        this.scene.add(pointLight)
    }

    initTestObject = () => {
        let geometry = new THREE.BoxGeometry( 1, 1, 1 );
        let material = new THREE.MeshStandardMaterial( { color: 0x00ff00 } );
        let cube = new THREE.Mesh( geometry, material );
        this.scene.add( cube );
    }

    addPlain = () =>{
        const geometry = new THREE.PlaneGeometry( 100, 100 );
        const material = new THREE.MeshStandardMaterial( {color: 0xffffff, side: THREE.DoubleSide} );
        const plane = new THREE.Mesh( geometry, material );
        plane.position.set(10,-1,10)
        plane.rotateX(Math.PI/2)
        this.scene.add( plane );
    }

    init = () => {
        //Scene
        this.scene = new THREE.Scene();

        //Size
        const sizes = {
            width: window.innerWidth,
            height: window.innerHeight
        }
        //Camera
        this.camera = new THREE.PerspectiveCamera(75, sizes.width / sizes.height, 0.1, 1000)
        this.camera.position.x = 50
        this.camera.position.y = 10
        this.camera.position.z = 0

        this.scene.add(this.camera)

        // Renderer
        this.renderer = new THREE.WebGLRenderer({antialias: true})
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
        this.renderer.outputEncoding = THREE.sRGBEncoding
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping
        this.renderer.toneMappingExposure = 0.5;

        this.initLights()
        this.initTestObject()
        this.addPlain()

//-------------
        window.addEventListener('resize', () => {
            // Update sizes
            sizes.width = window.innerWidth
            sizes.height = window.innerHeight

            // Update camera
            this.camera.aspect = sizes.width / sizes.height
            this.camera.updateProjectionMatrix()

            // Update renderer
            this.renderer.setSize(sizes.width, sizes.height)
            this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
        })

    }

    componentDidMount() {
        this.mount.appendChild(this.renderer.domElement); // mount a scene inside of React using a ref
    }

    render() {
        return(
            <div ref={ref => (this.mount = ref)}>

            </div>

        );
    }
}

export default Scene