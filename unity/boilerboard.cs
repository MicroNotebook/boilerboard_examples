using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO.Ports;

public class boilerboard : MonoBehaviour {

    SerialPort stream = new SerialPort("COM3", 115200);
	// Use this for initialization
	void Start () {
        stream.ReadTimeout = 1;
        stream.Open();
	}
	
	// Update is called once per frame
	void Update () {
        try {
            Debug.Log("Read " + stream.ReadChar());
        }
        catch {
            //Debug.Log("error");
        }
    }
}
