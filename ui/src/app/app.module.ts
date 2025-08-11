import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule, Routes } from '@angular/router';
import { AppComponent } from './app.component';
import { AskComponent } from './ask.component';
import { GoldensComponent } from './goldens.component';

const routes: Routes = [
  { path: '', component: AskComponent },
  { path: 'goldens', component: GoldensComponent },
  { path: '**', redirectTo: '' }
];

@NgModule({
  declarations: [AppComponent, AskComponent, GoldensComponent],
  imports: [BrowserModule, FormsModule, HttpClientModule, RouterModule.forRoot(routes)],
  bootstrap: [AppComponent]
})
export class AppModule {}
