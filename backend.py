import urllib.request as ur
import requests
from bs4 import BeautifulSoup
import sqlite3
import sys
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


class Backend:

    def __init__(self):
        page = ur.urlopen('https://en.wikipedia.org/wiki/List_of_countries_by_carbon_dioxide_emissions')
        page = requests.get('https://en.wikipedia.org/wiki/List_of_countries_by_carbon_dioxide_emissions')
        soup = BeautifulSoup(page.content, "lxml")
        self.countries = []
        self.string_emissions_percentage = []
        self.float_emissions = []
        self.emissions_1990 = []
        self.emissions_2005 = []
        self.emissions_2017 = []
        self.sorted_countries = []
        self.co2_change = []

        count1 = 0
        count2 = 0
        for info in soup.find_all('td', {'align': 'left'}):
            if info.find('a', title=True):
                for country in info.find('a', title=True):
                    self.countries.append(country)
                    count1 += 1
                for emission1990 in info.find_next('td'):
                    self.emissions_1990.append(emission1990)
                for emission2005 in info.find_next_sibling('td').find_next_sibling('td'):
                    self.emissions_2005.append(emission2005)
                for emission2017 in info.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td'):
                    self.emissions_2017.append(emission2017)
                for emission in info.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td'):
                    self.string_emissions_percentage.append(emission)
                    count2 += 1
                for change in info.find_next_sibling('td').find_next_sibling('td').find_next_sibling(
                    'td').find_next_sibling('td').find_next_sibling('td'):
                    self.co2_change.append(change)
            self.float_emissions = [float(i.strip('%')) for i in self.string_emissions_percentage]
        #print("1990", self.emissions_1990)
        #print("2005", self.emissions_2005)
        #print("2017", self.emissions_2017)
        #print("float emissions --->", self.float_emissions, "\n")
        print(count1, "Countries (Alphabetical Order)                         ", self.countries)
        print(count2, "Unsorted Emission Percentage                           ", self.string_emissions_percentage)
        self.sorted_country_emission = [(self.countries[i], self.float_emissions[i]) for i in range(0, len(self.countries))]
        self.sorted_country_emission.sort(key=lambda x: x[1], reverse=True)
        print("Sorted Countries by Emission Level tuple list              ", self.sorted_country_emission)
        for country in self.sorted_country_emission:
            self.sorted_countries.append(country[0])
        #print(self.sorted_countries)
        self.float_emissions.sort(key=lambda x: x, reverse=True)
        my_string = ','.join(map(str, self.float_emissions)).split(",")
        self.sorted_string_percentage = [val + "%" for val in my_string]
        #print(self.sorted_string_percentage)
        self.sorted_countries_by_percentage = list(zip(self.sorted_countries, self.sorted_string_percentage))
        print("Sorted Countries by % of World                             ", self.sorted_countries_by_percentage)
        print("Co2 differences between 1990 and 2017                      ", self.co2_change)

    def create_sql_table(self, file):
        self.conn = sqlite3.connect(file)
        self.cursor = self.conn.cursor()
    
        self.cursor.execute("DROP TABLE IF EXISTS emissions;")
        self.cursor.execute("CREATE TABLE emissions(country TEXT, emission TEXT);")
    
        for country in self.sorted_countries_by_percentage:
            self.cursor.execute("INSERT INTO emissions (country, emission) VALUES (?, ?)", (country[0], country[1]))
    
        self.conn.commit()

    def pie_chart_top_10_emissions(self):
        self.conn = sqlite3.connect('emissions.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM emissions")

        rows = self.cursor.fetchall()
        country_list = []
        emission_list = []

        for a in range(10):
            emission = list(map("".join, rows[a]))
            emission_list.append(emission[1])
            country_list.append(emission[0])
        strip_percent = []
        for change in emission_list:
            c = change.replace(',', '').strip('%')
            strip_percent.append(float(c))
        print("strip", strip_percent)

        legend_data = [list(i) for i in zip(country_list, emission_list)]
        font = {'family': 'normal',
                'weight': 'bold',
                'size': 22}
        plt.pie(strip_percent, explode=None, labels=country_list, autopct='%1.0f%%',
                shadow=True, startangle=90)
        plt.legend(legend_data, bbox_to_anchor=(0.1, 0.2, 0, 0), loc='best', prop={'size': 6})
        plt.axis('equal')

    def display_all_data(self, num_of_countries):
        plt.axis('off')
        columns = ['Countries', '1990 Emissions', '2005 Emission', '2017 Emission',
                   '2017 Levels(%)', '% 1990-2017']
        count = 0
        country_co2_percent = []
        em_1990 = []
        em_2005 = []
        em_2017 = []
        for value in range(len(self.emissions_1990)):
            em1 = float(self.emissions_1990[value].replace(',', ''))
            em_1990.append(em1)
            em2 = float(self.emissions_2005[value].replace(',', ''))
            em_2005.append(em2)
            em3 = float(self.emissions_2017[value].replace(',', ''))
            em_2017.append(em3)
        change_percentage = []
        for change in self.co2_change:
            c = change.replace(',', '').strip('%')
            change_percentage.append(float(c))
        print("Change Percent                                             ", change_percentage)

        for a in zip(self.countries, em_1990, em_2005, em_2017, self.string_emissions_percentage, self.co2_change):
            if count < num_of_countries:
                country_co2_percent.append(list(a))
                count += 1

        print("Emissions in 1990 (unsorted)                               ", em_1990)
        print("Emissions in 2005 (unsorted)                               ", em_2005)
        print("Emissions in 2017 (unsorted)                               ", em_2017)
        print("Emission Percentages in 2017 (unsorted)                    ", self.string_emissions_percentage)
        print("Country, Co2 in Diff Years, and Percent Emission           ", country_co2_percent)
        the_table = plt.table(cellText=country_co2_percent, colLabels=columns, loc='center')
        if num_of_countries == 3:
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(30/num_of_countries)
        elif num_of_countries == 6:
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(42/num_of_countries)
        elif num_of_countries == 9:
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(70/num_of_countries)
        elif num_of_countries == 15:
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(115/num_of_countries)
        elif num_of_countries == 18:
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(140/num_of_countries)
        elif num_of_countries == 30:
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(200/num_of_countries)

def main():
    emission = Backend()
    file = "emissions.db"
    emission.create_sql_table(file)
    emission.pie_chart_top_10_emissions()


if __name__ == '__main__':
    main()
