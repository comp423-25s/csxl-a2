import { Component, OnInit } from '@angular/core';
import { ChatbotDataService, Conversation } from './data.component.service';

@Component({
  selector: 'app-data',
  templateUrl: './data.component.html',
  styleUrls: ['./data.component.css']
})
export class DataComponent implements OnInit {
  constructor(private chatbotDataService: ChatbotDataService) {}

  conversations: Conversation[] = [];
  selectedSort: string = 'date-desc';
  visibleCount: number = 20;

  ngOnInit() {
    this.chatbotDataService.getAllConversations().subscribe({
      next: (data) => {
        this.conversations = data.map((c) => ({
          id: c.id,
          messages: (c as any).messages || (c as any).chat_history,
          rating: c.rating,
          date: (c as any).date || (c as any).created_at
        }));
      },
      error: (err) => {
        console.error('Error loading conversations:', err);
      }
    });
  }

  get sortedConversations(): Conversation[] {
    return [...this.conversations]
      .sort((a, b) => {
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
      })
      .slice(0, this.visibleCount);
  }

  onSortChange(sortValue: string) {
    this.selectedSort = sortValue;
    this.visibleCount = 20;
  }

  loadMore() {
    this.visibleCount += 20;
  }

  get hasMore(): boolean {
    return this.visibleCount < this.conversations.length;
  }
}
