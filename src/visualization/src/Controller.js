import React, { Component } from "react";

class Controller extends Component{

    constructor(props) {
        super(props);
    }

    toConnect = () =>{
        this.props.toConnect()
    }

    render() {
        return(
            <div>
                <input type='button' onClick={this.toConnect} value="CONNECT"/>
            </div>
        )
    }
}

export default Controller