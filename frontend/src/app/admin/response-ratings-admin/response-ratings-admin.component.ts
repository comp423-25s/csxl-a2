import { Component } from '@angular/core';
import { AdminDataService } from '../admin-data.service';

@Component({
  selector: 'app-response-ratings-admin',
  templateUrl: './response-ratings-admin.component.html',
  styleUrls: ['./response-ratings-admin.component.css']
})
export class ResponseRatingsAdminComponent {
  userId: number | null = null;
  conversations: any[] = [];
  averageRating: number | null = null;
  messageCountsByDate: { [date: string]: number } = {};

  constructor(private adminDataService: AdminDataService) {}

  searchUserConversations(): void {
    if (this.userId !== null) {
      this.adminDataService
        .getUserConversations(this.userId)
        .subscribe((data) => {
          this.conversations = data;

          // Calculate average rating + message count
          let total = 0;
          let count = 0;
          const dailyCounts: { [key: string]: number } = {};

          for (const convo of data) {
            for (const msg of convo.messages || []) {
              if (msg.rating != null) {
                total += msg.rating;
                count++;
              }
              const date = new Date(msg.timestamp).toLocaleDateString();
              dailyCounts[date] = (dailyCounts[date] || 0) + 1;
            }
          }

          this.averageRating = count > 0 ? total / count : null;
          this.messageCountsByDate = dailyCounts;
        });
    }
  }
}
