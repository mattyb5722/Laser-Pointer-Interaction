using AsyncIO;
using NetMQ;
using NetMQ.Sockets;
using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System;
using Boo.Lang;

public class HelloClient : MonoBehaviour{

    public GameObject img;
    private List<GameObject> images = new List<GameObject>();
    public Canvas canvas;
    private RequestSocket client;

    private void Start(){
        ForceDotNet.Force(); // this line is needed to prevent unity freeze after one use
        client = new RequestSocket();
        client.Connect("tcp://localhost:5555");
    }

    private void Update(){

        for (int i = 0; i < images.Count; i++)
        {
            Destroy(images[i]);
        }
        images.Clear();

        client.SendFrame("num_keypoints");
        int num_keypoints = Int32.Parse(client.ReceiveFrameString());

        for (int i = 0; i < num_keypoints; i++) { 
            client.SendFrame("Loc_x");
            string Loc_x = client.ReceiveFrameString();

            client.SendFrame("Loc_y");
            string Loc_y = client.ReceiveFrameString();

            Debug.Log("Loc_y: " + Loc_y + " Loc_x: " + Loc_x);

            int Pos_x = Int32.Parse(Loc_x);
            int Pos_y = Int32.Parse(Loc_y);

            GameObject temp = Instantiate(img);
            temp.transform.position = new Vector2(Pos_x, Pos_y);
            temp.transform.SetParent(canvas.transform);
            images.Add(temp);

        }
    }

    private void OnDestroy(){
        client.SendFrame("END");
        client.Disconnect("tcp://localhost:5555");
        client.Dispose();
        NetMQConfig.Cleanup(); // this line is needed to prevent unity freeze after one use
    }
}