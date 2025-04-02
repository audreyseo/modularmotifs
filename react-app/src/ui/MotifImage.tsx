import React, { useState, useEffect } from "react";
import './MotifImage.css'
// import axios from "axios";

interface MotifImageProps {
    motif_name: string;
    img_width: number;
}

const MotifImage: React.FC<MotifImageProps> = ({
    motif_name = "x-3x3",
    img_width = 100
}) => {
    const [imageSrc, setImageSrc] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchImage = async () => {
            try {
                
                


                const request = new Request(`http://127.0.0.1:5000/motif/${motif_name}`, {
                    method: "GET",
                    // mode: "cors",
                    // headers: {
                    //     "Access-Control-Allow-Origin": "http://localhost:3000"
                    // }
                })

                // const resonse = fetch(request)
                // .then(response => response.json())
                // .then(data => console.log("data", data))

                const response = await fetch(request);
                console.log(response)
                if (!response.ok) {
                    const text = await response.text();
                    throw new Error(`HTTP error! Status: ${response.status} ${text}`);
                }

                // const text = await response.text();
                // console.log("text", text)
                console.log("response", response)
                const blob = await response.json();
                console.log("blob", blob)
                // Convert blob to object URL
                // const imageUrl = URL.createObjectURL(blob);
                const imageUrl = `data:image/png;base64,${blob.data}`
                setImageSrc(imageUrl);
                console.log(imageUrl)
            } catch (err) {
                setError("Failed to fetch image.");
                console.error("Error fetching image:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchImage();
    }, [motif_name]);

    if (loading) return <p>{"Loading image..."}</p>;
    if (error) return <p style={{ color: "red" }}>{error}</p>;

    return (
        <tr className={"motif-image"}>
            {/* <h2>Fetched Image</h2> */}
            <td>{motif_name}</td>
            <td>{imageSrc && <img src={imageSrc} alt="Fetched from server" style={{ maxWidth: "100%" }} width={img_width} />}</td>
        </tr>
    );
};

export default MotifImage;