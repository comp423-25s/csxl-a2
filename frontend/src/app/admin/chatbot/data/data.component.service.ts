import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { PaginationParams, Paginated } from 'src/app/pagination';

export interface ChatbotConversation {
  id: number;
  messages: string[];
  rating: number;
  date: string;
}

@Injectable({ providedIn: 'root' })
export class ChatbotDataService {
  constructor(private http: HttpClient) {}

  list(params: PaginationParams) {
    const paramStrings = {
      page: params.page.toString(),
      page_size: params.page_size.toString(),
      order_by: params.order_by,
      filter: params.filter
    };
    const query = new URLSearchParams(paramStrings);
    return this.http.get<Paginated<ChatbotConversation, PaginationParams>>(
      `/api/admin/chatbot-data?${query.toString()}`
    );
  }
}
