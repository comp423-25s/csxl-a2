import { Component } from '@angular/core';
import { Route } from '@angular/router';
import { ChatbotDataService } from './data.component.service';

interface Conversation {
  id: number;
  messages: string[];
  rating: number;
  date: string;
}

@Component({
  selector: 'app-data',
  templateUrl: './data.component.html',
  styleUrls: ['./data.component.css']
})
export class DataComponent {
  constructor(private chatbotDataService: ChatbotDataService) {}

  conversations: Conversation[] = [
    {
      id: 1,
      messages: ['Hi there!', 'How can I help you today?', 'Thanks!'],
      rating: 4,
      date: '2025-04-29T14:30:00Z'
    },
    {
      id: 2,
      messages: ['What time does the library open?', '8am to 10pm daily.'],
      rating: 5,
      date: '2025-04-28T10:15:00Z'
    },
    {
      id: 3,
      messages: [
        'Tell me a joke',
        "Why don't eggs tell secrets? They might crack up!"
      ],
      rating: 2,
      date: '2025-05-01T09:00:00Z'
    }
  ];

  selectedSort: string = 'date-desc';

  get sortedConversations(): Conversation[] {
    return [...this.conversations].sort((a, b) => {
      switch (this.selectedSort) {
        case 'date-asc':
          return new Date(a.date).getTime() - new Date(b.date).getTime();
        case 'date-desc':
          return new Date(b.date).getTime() - new Date(a.date).getTime();
        case 'rating-asc':
          return a.rating - b.rating;
        case 'rating-desc':
          return b.rating - a.rating;
        default:
          return 0;
      }
    });
  }

  onSortChange(sortValue: string) {
    this.selectedSort = sortValue;
  }
}
