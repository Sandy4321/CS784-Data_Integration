package com.walmart.productgenome.matching.models.rules.functions;

import com.walmart.productgenome.matching.models.rules.functions.Function.ArgType;

import uk.ac.shef.wit.simmetrics.similaritymetrics.AbstractStringMetric;
import uk.ac.shef.wit.simmetrics.similaritymetrics.Levenshtein;

public class LevenshteinSimilarity extends Function {

	public static final String NAME = "LEVENSHTEIN";
	public static final String DESCRIPTION = "Normalised Levenshtein Similarity";
	public static final int NUM_ARGS = 2;
	
	public LevenshteinSimilarity() {
		super(NAME, DESCRIPTION);
	}

	public LevenshteinSimilarity(String name, String description) {
		super(name, description);
	}

	@Override
	public Object compute(String[] args) throws IllegalArgumentException {
		if(args.length != NUM_ARGS){
			throw new IllegalArgumentException("Expected number of arguments: " + NUM_ARGS);
		}
		AbstractStringMetric metric = new Levenshtein();
		return metric.getSimilarity(args[0], args[1]);
	}

  @Override
  public ArgType getArgType() {
    return ArgType.STRING;
  }
  
	@Override
	public String getSignature() {
		StringBuilder sb = new StringBuilder();
		sb.append(this.getName());
		sb.append(",");
		sb.append(this.getDescription());
		sb.append(",");
		sb.append(this.getClass().getName());
		sb.append(",");
		sb.append(Float.class.getName());
		sb.append(",");
		sb.append(NUM_ARGS);
		sb.append(",");
		sb.append(String.class.getName());
		sb.append(",");
		sb.append(String.class.getName());
		return sb.toString();
	}

}
