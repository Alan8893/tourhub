# TourHub Features Documentation

## Overview

TourHub is an ERP platform for tourist clubs.

The main purpose:


Reduce preparation time for hiking trips
through automation of planning and calculations.


---

# Current MVP Features

## Nutrition Planning

Status:


IMPLEMENTED


The system provides the foundation for automatic food preparation.

---

# Product Management

Status:


IMPLEMENTED


## Purpose

Store products used for hiking meals.

Examples:


Rice

Buckwheat

Pasta

Meat

Tea


---

Capabilities:

- product name;
- category;
- measurement unit;
- package size.

---

# Recipe Management

Status:


IMPLEMENTED


## Purpose

Store meal compositions.

Example:


Camp pilaf


Composition:


Rice

Meat

Oil


---

A recipe defines:


what products

and

how much per person


---

# Dish Management

Status:


IMPLEMENTED


## Purpose

Represent menu-level meals.

Example:


Dinner:

Camp pilaf


---

Relationship:


Dish

↓

Recipe

↓

Ingredients

↓

Products


---

# Shopping List Calculation

Status:


IMPLEMENTED


## Purpose

Calculate required products for a group trip.

---

Input:


Recipe

Participants

Days


---

Output:


Product

Quantity

Unit


---

Example:

Input:


Rice:

120 g/person

10 people

5 days


Calculation:


120 × 10 × 5

=

6000 g


Result:


Rice:

6000 g


---

# Shopping List Service

Status:


IMPLEMENTED


## Purpose

Connect business calculation with database data.

Flow:


Database

↓

ORM Models

↓

Shopping Service

↓

Calculation Engine

↓

Shopping Result


---

# Seed Data

Status:


IMPLEMENTED


Initial dataset:


Products:
11

Recipes:
5

Dishes:
5


---

# Planned Features

---

# Meal Plan Generator

Status:


NEXT


## Goal

Automatically generate hiking menu.

---

Input:


Participants count

Number of days

Starting meal


---

Output:


Daily menu

Dishes

Recipes

Shopping list


---

## Rules

Generator should:

- avoid repeated dishes;
- use available recipes;
- provide warnings if database is insufficient;
- allow future manual replacement.

---

# Nutrition Wizard

Status:


PLANNED


User flow:


Step 1

Participants

    ↓

Step 2

Duration

    ↓

Step 3

Meal start

    ↓

Step 4

Generate menu

    ↓

Step 5

Review shopping list


---

# Packaging Management

Status:


PLANNED


## Purpose

Prepare products for carrying.

Features:

- package division;
- weight calculation;
- group bags;
- personal packages.

---

Example:


Buckwheat required:

3200 g

Package:

900 g

Result:

4 packages


---

# Purchase Management

Status:


PLANNED


Features:

- shopping checklist;
- purchased status;
- supplier information;
- price tracking.

---

# Export System

Status:


PLANNED


Formats:


PDF

Excel

Print


---

Possible exports:

## Shopping List


Product

Quantity

Package count


---

## Packing List


Item

Weight

Responsible person


---

# Hiking Project Management

Status:


PLANNED


## Purpose

Create a central object representing trip preparation.

Entity:


Project


---

Contains:


Route

Participants

Meal Plan

Equipment

Documents


---

# Route Management

Status:


PLANNED


Features:

- route description;
- map links;
- coordinates;
- difficulty;
- comments.

---

# Equipment Management

Status:


PLANNED


Features:

- equipment database;
- packing lists;
- personal equipment;
- group equipment.

---

# User Management

Status:


PLANNED


---

Roles:

## Guest

Capabilities:

- view public information.

---

## Instructor

Capabilities:

- create trips;
- generate plans;
- manage preparation.

---

## Verified Instructor

Capabilities:

- publish trips;
- manage club resources.

---

## Administrator

Capabilities:

- manage users;
- manage clubs;
- configure system.

---

# Multi Club Support

Status:


PLANNED


TourHub is designed for multiple tourist organizations.

Structure:


Club

↓

Users

↓

Projects

↓

Trips


---

# Future Advanced Features

---

## Analytics

Possible:

- trip statistics;
- food consumption;
- expenses;
- history.

---

## Mobile Application

Possible:

- hiking checklist;
- offline mode;
- trip assistant.

---

## AI Assistant

Future possibilities:

- suggest menus;
- optimize weight;
- recommend products;
- analyze previous trips.

---

# Feature Development Principles

## Business Value First

Features are developed according to real user scenarios.

---

## Automation Over Manual Work

The system should remove repetitive preparation tasks.

---

## Reliable Calculations

All generated results must be:

- predictable;
- reproducible;
- tested.

---

# Current Feature Status

Implemented:


Backend Foundation ✅

Nutrition Domain ✅

Products ✅

Recipes ✅

Dishes ✅

Shopping Calculation ✅

Shopping Service ✅


Next:


Meal Plan Generator


First complete user scenario:


Generate hiking food plan automatically