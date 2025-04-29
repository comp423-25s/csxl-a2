import { Component } from '@angular/core';

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

  constructor() {}

  searchUserConversations(): void {
    // TODO: Call backend to get conversations for this.userId
    console.log('Searching conversations for user ID:', this.userId);
  }
}
