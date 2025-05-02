import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-room-availability-widget',
  templateUrl: './room-availability-widget.component.html',
  styleUrls: ['./room-availability-widget.component.css']
})
export class RoomAvailabilityWidgetComponent implements OnInit {
  availableRooms: string[] = [];

  constructor() {}

  ngOnInit(): void {
    // TODO: Call service to load room availability here
  }
}
