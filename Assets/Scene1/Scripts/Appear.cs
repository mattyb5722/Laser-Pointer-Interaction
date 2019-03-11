using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using Boo.Lang;

public class Appear : MonoBehaviour {

    //public Image img;
    public GameObject img1;
    public Canvas canvas;
    private List<GameObject> images = new List<GameObject>();

    // Use this for initialization
    void Start () {
        for (int i = 0; i < 5; i++){
            GameObject temp = Instantiate(img1);
            temp.transform.position = new Vector2(i*50, i*50);
            temp.transform.SetParent(canvas.transform);
            images.Add(temp);
        }
    }

	// Update is called once per frame
	void Update () {
        if (Input.GetKeyDown("i")){
            for (int i = 0; i < images.Count; i++){
                Destroy(images[i]);
            }
            Debug.Log(images.Count);
            images.Clear();
            Debug.Log(images.Count);
        }
    }
}