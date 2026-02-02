#include <iostream>
#include <vector>
#include <climits>
using namespace std;

int main() {
    vector<int> L1 = {1,2,2,3,5,5,9,10,10};

    // Step 1: Remove duplicates (manual)
    vector<int> uniqueList;

    for(int i = 0; i < L1.size(); i++) {
        bool found = false;

        for(int j = 0; j < uniqueList.size(); j++) {
            if(L1[i] == uniqueList[j]) {
                found = true;
                break;
            }
        }

        if(!found) uniqueList.push_back(L1[i]);
    }

    // Step 2: Find largest and second largest
    int largest = INT_MIN;
    int secondLargest = INT_MIN;

    for(int i = 0; i < uniqueList.size(); i++) {
        int x = uniqueList[i];

        if(x > largest) {
            secondLargest = largest;
            largest = x;
        }
        else if(x > secondLargest && x != largest) {
            secondLargest = x;
        }
    }

    cout << "Second largest number: " << secondLargest << endl;

    return 0;
}
