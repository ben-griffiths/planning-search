import React, { useEffect, useRef } from "react";

export const MapResult = ({ results }) => {
  const mapRef = useRef(null);

  useEffect(() => {
    if (!window.google) {
      console.error("Google Maps JavaScript API not loaded.");
      return;
    }

    // Calculate the average latitude and longitude
    const validResults = results.filter((result) => result.location);
    if (validResults.length === 0) {
      return; // No valid results with location data
    }

    const locations = validResults.map((result) => result.location);
    const latLngList = locations.map((location) => {
      const [lat, lng] = location.split(",");
      return new window.google.maps.LatLng(parseFloat(lat), parseFloat(lng));
    });
    const bounds = new window.google.maps.LatLngBounds();
    bounds.extend(latLngList[0]);
    const center = bounds.getCenter();

    // Initialize the map
    const map = new window.google.maps.Map(mapRef.current, {
      center: center,
      zoom: 10,
    });

    // Add markers for each result
    validResults.forEach((result) => {
      const location = result.location.split(",");
      const lat = parseFloat(location[0]);
      const lng = parseFloat(location[1]);

      // Create marker
      const marker = new window.google.maps.Marker({
        position: { lat, lng },
        map,
      });

      // Create info window
      const infoWindow = new window.google.maps.InfoWindow({
        content: `<div>
          <h2>${result.reference_no}</h2>
          <p>${result.address}</p>
          <p>${result.validation_date}</p>
          <p>${result.proposal}</p>
        </div>`,
      });

      // Add click event listener to open info window
      marker.addListener("click", () => {
        infoWindow.open(map, marker);
      });
    });
  }, [results]);

  return <div ref={mapRef} style={{ width: "100%", height: "400px" }} />;
};
