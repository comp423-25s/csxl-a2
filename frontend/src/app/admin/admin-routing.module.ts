import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AdminUsersRolesComponent } from './accounts/admin-accounts.component';
import { AdminRoleDetailsComponent } from './accounts/roles/details/admin-role-details.component';
import { AdminRolesListComponent } from './accounts/roles/list/admin-roles-list.component';
import { AdminUsersListComponent } from './accounts/users/admin-users.component';
import { AdminComponent } from './admin.component';
import { permissionGuard } from '../permission.guard';
import { RoomAvailabilityAdminComponent } from './room-availability-admin/room-availability-admin.component';
import { ResponseRatingsAdminComponent } from './response-ratings-admin/response-ratings-admin.component';

const routes: Routes = [
  {
    path: '',
    title: 'Site Administration',
    component: AdminComponent,
    canActivate: [permissionGuard('admin.*', '*')]
  },
  {
    path: 'accounts',
    component: AdminUsersRolesComponent,
    children: [
      AdminUsersListComponent.Route,
      AdminRolesListComponent.Route,
      AdminRoleDetailsComponent.Route
    ]
  },
  { path: 'room-availability', component: RoomAvailabilityAdminComponent },
  { path: 'response-ratings', component: ResponseRatingsAdminComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AdminRoutingModule {}
