import { Component, OnInit } from '@angular/core';
import { AdminDataService } from '../admin-data.service';

@Component({
  selector: 'app-room-availability-admin',
  templateUrl: './room-availability-admin.component.html',
  styleUrls: ['./room-availability-admin.component.css']
})
export class RoomAvailabilityAdminComponent implements OnInit {
  rooms: any[] = [];

  constructor(private adminDataService: AdminDataService) {}

  ngOnInit(): void {
    this.loadRooms();
  }

  loadRooms(): void {
    this.adminDataService.getAllRooms().subscribe((data) => {
      this.rooms = data;
    });
  }

  toggleAvailability(room: any): void {
    const newAvailability = !room.available;
    this.adminDataService
      .updateRoomAvailability(room.id, newAvailability)
      .subscribe(() => {
        room.available = newAvailability; // Update locally after success
      });
  }
}
